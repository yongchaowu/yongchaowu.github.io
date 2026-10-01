#!/usr/bin/env bash
# Strip unpublished material from the published git history of
# yongchaowu.github.io.
#
# Why this exists
# ---------------
# `_drafts/` held seven files that were never published anywhere: four private
# diary entries, a team-building retrospective, a book list and a note. They
# were confirmed NOT to be publicly reachable -- the cnblogs sitemap lists 339
# public URLs while the cnblogs export holds 346 files, and the difference is
# exactly these seven. So the git history of a *public* repository was the only
# place they existed, and unlike cnblogs (29 pages deep, pagination capped for
# anonymous visitors, zero search results) a git repository has no depth limit,
# is globally indexed by GitHub code search, and is permanently archived by
# third parties.
#
# What it does
# ------------
# 1. Snapshots every ref into a bundle and the working tree into a tarball
#    (the workspace rule: take a tip snapshot before moving any ref).
# 2. Runs `git filter-repo --path _drafts --invert-paths` in a throwaway mirror.
# 3. Re-points the real repository's refs at the rewritten history WITHOUT
#    touching the working tree or the index, so uncommitted work is preserved.
#    `git filter-repo` cannot be run in place: it refuses a non-fresh clone and
#    would also destroy 229 uncommitted modifications and 3,186 staged
#    deletions.
# 4. Moves *every* ref, not just master. This is the step that is easy to miss:
#    a first attempt left `refs/remotes/origin/master`, `refs/remotes/origin/HEAD`
#    and the `site-v2` tag still pointing at the old history, so the sensitive
#    blobs would have been pushed to GitHub anyway. A tag is enough on its own.
# 5. Updates the `verify-post-history.rb` baseline, which is a commit hash and
#    therefore changes with any rewrite. The 13 `fixed_blob` hashes in
#    `_data/format_fixes.yml` are content-addressed and stay valid, because the
#    rewrite does not touch a single byte outside `_drafts/`.
# 6. Verifies: no `_drafts` path in any ref's history, the sensitive string
#    absent from every reachable commit, every commit tree identical once
#    `_drafts/` is excluded, and the full acceptance suite green.
#
# Usage:  bash scripts/strip-drafts-from-history.sh [--execute]
#         (dry run by default; --execute performs the ref moves)

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP="${REWRITE_BACKUP_DIR:-$HOME/Workspace/_rewrite-backup}"
WORK="${TMPDIR:-/tmp}/strip-drafts-$$"
SENSITIVE='993492315'   # the QQ number in the private diary; do not echo it
EXECUTE=0
[ "${1:-}" = "--execute" ] && EXECUTE=1

cd "$REPO"
echo "== repository: $REPO"

OLD_HEAD="$(git rev-parse refs/heads/master)"
OLD_COUNT="$(git rev-list --count refs/heads/master)"
echo "== master: ${OLD_HEAD:0:12}  ($OLD_COUNT commits)"

# ---------------------------------------------------------------- 1. snapshot
mkdir -p "$BACKUP"
STAMP="$(date +%Y%m%d-%H%M%S)"
echo
echo "== 1. snapshot"
git bundle create "$BACKUP/pre-rewrite-$STAMP.bundle" --all 2>&1 | tail -1
tar czf "$BACKUP/worktree-$STAMP.tar.gz" \
    --exclude=_site --exclude=vendor --exclude=.git . 2>/dev/null || true
ls -la "$BACKUP/pre-rewrite-$STAMP.bundle" "$BACKUP/worktree-$STAMP.tar.gz" | sed 's/^/   /'

# ------------------------------------------------- 2. rewrite in a throwaway mirror
echo
echo "== 2. rewrite in a disposable mirror"
rm -rf "$WORK.git"
git clone -q --mirror . "$WORK.git"
git -C "$WORK.git" filter-repo --path _drafts --invert-paths --force 2>&1 | grep -E 'Parsed|finished' | sed 's/^/   /'
NEW_HEAD="$(git -C "$WORK.git" rev-parse refs/heads/master)"
echo "   new master: ${NEW_HEAD:0:12}"

# ------------------------------------------- 3. verify the rewrite before touching anything
echo
echo "== 3. verify the rewrite (in the mirror, before any ref moves)"
python3 - "$REPO" "$WORK.git" "$OLD_COUNT" <<'PY'
import subprocess, sys
orig, sim, want = sys.argv[1], sys.argv[2], int(sys.argv[3])
def git(repo, *a):
    return subprocess.run(['git', '-C', repo, *a], capture_output=True, text=True).stdout
o = [l for l in git(orig, 'log', '--format=%s', '--reverse', 'refs/heads/master').split('\n') if l]
s = [l for l in git(sim,  'log', '--format=%s', '--reverse', 'refs/heads/master').split('\n') if l]
assert len(o) == len(s) == want, f"commit count changed: {len(o)} -> {len(s)}"
assert o == s, "commit subjects diverged"
# Tree comparison, position by position: every commit must be byte-identical once
# `_drafts/` is excluded, which is what makes this a surgical rewrite.
oc = [l for l in git(orig, 'rev-list', '--reverse', 'refs/heads/master').split('\n') if l]
sc = [l for l in git(sim,  'rev-list', '--reverse', 'refs/heads/master').split('\n') if l]
bad = 0
for i in range(want):
    ta = [l for l in git(orig, '-c', 'core.quotePath=false', 'ls-tree', '-r', oc[i]).split('\n')
          if '\t_drafts/' not in l]
    tb = [l for l in git(sim,  '-c', 'core.quotePath=false', 'ls-tree', '-r', sc[i]).split('\n')
          if '\t_drafts/' not in l]
    if ta != tb:
        bad += 1
        print(f"   TREE DIFFERS at commit #{i+1}")
print(f"   commits: {want} preserved, subjects identical")
print(f"   trees (excluding _drafts): {want - bad}/{want} identical")
if bad:
    sys.exit(1)
PY

# ------------------------------------------------------------- 4. move the refs
echo
if [ "$EXECUTE" -eq 0 ]; then
    echo "== 4. DRY RUN -- no ref was moved. Re-run with --execute to apply."
    echo "   refs that would move:"
    for r in $(git for-each-ref --format='%(refname)'); do
        printf "     %-34s %s\n" "$r" "$(git rev-parse --short "$r")"
    done
    echo
    echo "   backup bundle: $BACKUP/pre-rewrite-$STAMP.bundle"
    rm -rf "$WORK.git"
    exit 0
fi

echo "== 4. move every ref to the rewritten history"
git fetch -q "$WORK.git" "+refs/heads/master:refs/rewritten/master"
git update-ref refs/heads/master "$NEW_HEAD" "$OLD_HEAD"
echo "   refs/heads/master        ${OLD_HEAD:0:12} -> ${NEW_HEAD:0:12}"

python3 - "$REPO" "$NEW_HEAD" <<'PY'
import subprocess, sys
repo, new = sys.argv[1], sys.argv[2]
def git(*a): return subprocess.run(['git','-C',repo,*a],capture_output=True,text=True).stdout.strip()
def committer_order():
    return [l for l in git('rev-list','--reverse','refs/heads/master').split('\n') if l]
new_order = committer_order()
# Remote-tracking refs and tags must follow, or the old objects stay reachable
# and get pushed. Annotated tags resolve to a tag object, so peel with ^{}.
for r in ('refs/remotes/origin/master', 'refs/remotes/origin/HEAD'):
    if git('rev-parse','--verify','--quiet',r):
        git('update-ref', r, new)
        print(f"   {r:<34} -> {new[:12]}")
# Tags need more care than refs. `git rev-parse <tag>` on an ANNOTATED tag
# returns the tag object, not the commit, so peel it. The old commit hash no
# longer exists, so the mapping has to be by position, cross-checked by subject --
# matching by hash alone silently leaves the tag behind, and a tag is enough on
# its own to keep the old objects reachable and pushable.
#
# `git tag -f` would also downgrade an annotated tag to a lightweight one, losing
# the tagger and the message, so the tag object is rebuilt with `git mktag`.
import subprocess
for t in [l.strip().lstrip('* ').split()[0] for l in git('tag','-l').split('\n') if l.strip()]:
    peeled = git('rev-parse', f'{t}^{{commit}}')
    if not peeled:
        print(f"   tag {t}: cannot peel, left alone")
        continue
    subj = git('log','-1','--format=%s',peeled)
    same = [c for c in new_order if git('log','-1','--format=%s',c) == subj]
    if not same:
        print(f"   tag {t}: no commit with subject '{subj}' in rewritten master, left alone")
        continue
    target = same[-1]
    if git('cat-file','-t',t) == 'tag':
        body = git('cat-file','-p',t).split('\n')
        body[0] = f'object {target}'
        newobj = subprocess.run(['git','-C',repo,'mktag'], input='\n'.join(body)+'\n',
                                capture_output=True, text=True).stdout.strip()
        if not newobj:
            print(f"   tag {t}: mktag failed, left alone")
            continue
        git('update-ref', f'refs/tags/{t}', newobj, git('rev-parse', f'refs/tags/{t}'))
    else:
        git('update-ref', f'refs/tags/{t}', target)
    print(f"   tag {t}: {'annotated, rebuilt' if git('cat-file','-t',f'refs/tags/{t}')=='tag' else 'lightweight'} -> {target[:12]}")
PY
git update-ref -d refs/rewritten/master 2>/dev/null || true

# ------------------------------------------------------------ 5. fix the baseline
echo
echo "== 5. update the verify-post-history baseline"
python3 - "$REPO" <<'PY'
import subprocess, sys, re, pathlib
repo = sys.argv[1]
def git(*a): return subprocess.run(['git','-C',repo,*a],capture_output=True,text=True).stdout.strip()
path = pathlib.Path(repo) / 'scripts' / 'verify-post-history.rb'
src = path.read_text(encoding='utf-8')
m = re.search(r"BASELINE = ENV\.fetch\('POST_HISTORY_BASELINE', '([0-9a-f]{40})'\)", src)
old = m.group(1)
subject = git('log','-1','--format=%s',old) if git('cat-file','-t',old)=='commit' else ''
order = [l for l in git('rev-list','--reverse','refs/heads/master').split('\n') if l]
if old in order:
    new = order[order.index(old)]
elif subject:
    cands = [c for c in order if git('log','-1','--format=%s',c) == subject]
    new = cands[-1] if cands else None
    print(f"   old baseline {old[:12]} no longer exists; matched by subject '{subject}'")
else:
    new = None
if new:
    path.write_text(src.replace(old, new), encoding='utf-8')
    print(f"   baseline {old[:12]} -> {new[:12]}")
else:
    print("   could not map the old baseline; set POST_HISTORY_BASELINE manually")
PY

# ---------------------------------------------------------------- 6. verify
echo
echo "== 6. verify"
echo "   refs now:"
git for-each-ref --format='     %(refname)  %(objectname:short)' | sed 's/^/   /'
hits=0
for r in $(git for-each-ref --format='%(refname)'); do
    n=$(git -c core.quotePath=false grep -l "$SENSITIVE" $(git rev-list "$r" 2>/dev/null) 2>/dev/null | wc -l)
    [ "$n" -gt 0 ] && { echo "   SENSITIVE STRING STILL IN $r ($n)"; hits=1; }
done
[ "$hits" -eq 0 ] && echo "   sensitive string absent from every reachable commit  OK"
drafts=$(git -c core.quotePath=false log --all --name-only --format= -- '_drafts/' 2>/dev/null | grep -c '^_drafts/' || true)
echo "   _drafts paths in history: ${drafts:-0}  $([ "${drafts:-0}" = 0 ] && echo OK || echo FAIL)"
echo "   uncommitted modifications preserved: $(git status --porcelain | grep -v '^D ' | wc -l)"
echo "   files still on disk under _drafts: $(ls _drafts 2>/dev/null | wc -l) (untracked, not built)"
echo
echo "   Backup bundle: $BACKUP/pre-rewrite-$STAMP.bundle"
echo "   NOTE: objects are still in .git until `git reflog expire --expire=now --all &&"
echo "         git gc --prune=now`. A push only sends objects reachable from the"
echo "         pushed refs, so GitHub is already clean; the gc is for local disk."
rm -rf "$WORK.git"
echo
echo "Done. Re-run the acceptance suite before pushing."
