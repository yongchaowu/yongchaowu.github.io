---
layout: post
title: "Code-CSDN-C++-图"
date: 2024-06-11 06:44:00
categories: ["Code"]
tags: ["Code", "Data Structure"]
---

**转自**
版权声明：本文为博主原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接和本声明。
本文链接：https://blog.csdn.net/weixin_62684026/article/details/128358023

<!--more-->
---
## Code

### 数据结构

#### 邻接表

```c++
namespace link_table
{
    //创建边的结构
    template<class W>
    struct Edge
    {
        //int _srci;这里我们暂且不存源点的下标
        int _dsti;  // 目标点的下标
        W _w;		// 权值
        Edge<W>* _next;//邻接表的链接指针

        Edge(int dsti, const W& w)
                :_dsti(dsti)
                , _w(w)
                , _next(nullptr)
        {}
    };

    template<class V, class W, bool Direction = false>
    class Graph
    {
        typedef Edge<W> Edge;
    public:
        Graph(const V* a, size_t n)
        {
            _vertexs.reserve(n);
            for (size_t i = 0; i < n; ++i)
            {
                _vertexs.push_back(a[i]);
                _indexMap[a[i]] = i;
            }

            _tables.resize(n, nullptr);
        }

        size_t GetVertexIndex(const V& v)
        {
            auto it = _indexMap.find(v);
            if (it != _indexMap.end())
            {
                return it->second;
            }
            else
            {
                //assert(false);
                throw invalid_argument("顶点不存在");

                return -1;
            }
        }

        void AddEdge(const V& src, const V& dst, const W& w)
        {
            size_t srci = GetVertexIndex(src);
            size_t dsti = GetVertexIndex(dst);

            // 1->2
            Edge* eg = new Edge(dsti, w);
            //头插法
            eg->_next = _tables[srci];
            _tables[srci] = eg;

            // 2->1
            // 如果是无向图的话，添加反向的路径
            if (Direction == false)
            {
                Edge* eg = new Edge(srci, w);
                eg->_next = _tables[dsti];
                _tables[dsti] = eg;
            }
        }

        void Print()
        {
            // 顶点
            for (size_t i = 0; i < _vertexs.size(); ++i)
            {
                cout << "[" << i << "]" << "->" << _vertexs[i] << endl;
            }
            cout << endl;

            for (size_t i = 0; i < _tables.size(); ++i)
            {
                cout << _vertexs[i] << "[" << i << "]->";
                Edge* cur = _tables[i];
                while (cur)
                {
                    cout <<"["<<_vertexs[cur->_dsti] << ":" << cur->_dsti << ":"<<cur->_w<<"]->";
                    cur = cur->_next;
                }
                cout <<"[nullptr]"<<endl;
            }
        }

    private:
        vector<V> _vertexs;			// 顶点集合
        map<V, int> _indexMap;		// 顶点映射下标
        vector<Edge*> _tables;		// 邻接表
    };

    void TestGraph1()
    {
        /*Graph<char, int, true> g("0123", 4);
        g.AddEdge('0', '1', 1);
        g.AddEdge('0', '3', 4);
        g.AddEdge('1', '3', 2);
        g.AddEdge('1', '2', 9);
        g.AddEdge('2', '3', 8);
        g.AddEdge('2', '1', 5);
        g.AddEdge('2', '0', 3);
        g.AddEdge('3', '2', 6);

        g.Print();*/

        string a[] = { "张三", "李四", "王五", "赵六" };
        Graph<string, int, true> g1(a, 4);
        g1.AddEdge("张三", "李四", 100);
        g1.AddEdge("张三", "王五", 200);
        g1.AddEdge("王五", "赵六", 30);
        g1.Print();
    }
}

```

#### 邻接矩阵
```c++
#pragma once
#include <vector>
#include <map>
//V表示的事我们点中的数据类型
// weight代表权重
//Direction表示是有向图还是无向图
namespace matrix
{
    //我们这里默认是无向图
    template<class V,class W ,W MAX_W=INT_MAX, bool Direction =false>
    class Graph
    {
    public:
        //图的创建
        //1、IO输入 --不方便测试,oj中更适合
        //2、图结构关系样例写到文件里，读取文件
        //3.手动添加边（首先我们创建顶点，手动添加边）
        Graph(const V*a,size_t n)
        {
            _vertex.reserve(n);
            for(size_t i=0;i<n;++i)
            {
                _vertex.push_back(a[i]);
                //通过顶点找下标
                _indexmap[a[i]]=i;
            }
            _matrix.resize(n);
            for(size_t i=0;i<_matrix.size();++i) {
                //开辟n个大小，然后初始化每一个值都是MAX_W
                _matrix[i].resize(n, MAX_W);
            }
        }
        //确定顶点的下标
        size_t  GetVertexIndex(const V& v)
        {
            auto it=_indexmap.find(v);
            //如果查找到了就返回下标
            if( it!=_indexmap.end())
            {
                return it->second;
            }else
            {
//                assert(false);
                throw invalid_argument("顶点不存在");
                //防止编译器检查
                return -1;

            }
        }
        void AddEdge(const V& src,const V&dst,const W& w)
        {
            size_t srci= GetVertexIndex(src);
            size_t dsti= GetVertexIndex(dst);

            _matrix[srci][dsti]=w;
            //如果是无向图的话，我们需要添加双向的
            if(Direction== false)
            {
                _matrix[dsti][srci]=w;
            }
        }

        void Print()
        {
            //将顶点打印出来
            for(size_t i=0;i<_vertex.size();++i)
            {
                cout<<"["<<i<<"]"<<"->"<<_vertex[i]<<endl;

            }
            cout<<endl;

            //矩阵
            //将横向的下标打印出来
            cout<<"  ";
            for(size_t i=0;i<_vertex.size();++i)
            {
                cout<<i<<" ";
            }
            cout<<endl;
            for(size_t i=0;i<_matrix.size();++i)
            {
                cout<<i<<" ";//将竖向的下标打印出来
                for(size_t j=0;j<_matrix[i].size();++j)
                {
//                    cout<<_matrix[i][j]<<" ";
                    if(_matrix[i][j]==MAX_W)
                    {
                        cout<<"* ";
                    }
                    else{
                        cout<<_matrix[i][j]<<" ";
                    }
                }
                cout<<endl;
            }
        }


    private:
        vector<V> _vertex;//顶点集合
        map<V,int> _indexmap;//顶点映射下标
        vector<vector<W>> _matrix; //邻接矩阵
    };
    void TestGraph() {
        Graph<char, int, INT_MAX, true> g("0123", 4);
        g.AddEdge('0', '1', 1);
        g.AddEdge('0', '3', 4);
        g.AddEdge('1', '3', 2);
        g.AddEdge('1', '2', 9);
        g.AddEdge('2', '3', 8);
        g.AddEdge('2', '1', 5);
        g.AddEdge('2', '0', 3);
        g.AddEdge('3', '2', 6);
        g.Print();
    }
}

```

---

### 遍历

#### 深度优先遍历

```c++
void _DFS(size_t srci, vector<bool>& visited)
        {
            //访问一个点，标记一个点
            cout << srci << ":" << _vertex[srci] << endl;
            visited[srci] = true;

            // 找一个srci相邻的没有访问过的点，去往深度遍历
            for (size_t i = 0; i < _vertex.size(); ++i)
            {
                if (_matrix[srci][i] != MAX_W && visited[i] == false)
                {
                    _DFS(i, visited);
                }
            }

        }

        void DFS(const V& src)
        {
            //获取传入的源点的下标
            size_t srci = GetVertexIndex(src);
            //创建标记数组
            vector<bool> visited(_vertex.size(), false);

            _DFS(srci, visited);
        }

```

#### 广度优先遍历
```c++
//传入起点`
        void BFS(const V& src)
        {
            //计算起点的下标
        	size_t srci = GetVertexIndex(src);

        	// 队列和标记数组
        	queue<int> q;
            //创建一个标记数组
        	vector<bool> visited(_vertex.size(), false);

            //将起点加入队列中
        	q.push(srci);
            //标记起点
            //只要入队列了，我们就将其标记
        	visited[srci] = true;

        	size_t n = _vertex.size();
        	while (!q.empty())
        	{
                //出队头的数据
        		int front = q.front();
        		q.pop();
        		cout << front <<":"<<_vertex[front] << endl;
        		// 把front顶点的邻接顶点入队列
        		for (size_t i = 0; i < n; ++i)
        		{
        			if (_matrix[front][i] != MAX_W)
        			{
                        //如果没有被标记过，我们就将其入队
        				if (visited[i] == false)
        				{
        					q.push(i);
        					visited[i] = true;
        				}
        			}
        		}
        	}

        	cout << endl;
        }

```


---


### 最小生成树

#### Kruskal算法（克鲁斯卡尔算法）
```c++
//边的定义，源点，目标点，权值
        struct Edge
        {
            size_t _srci;
            size_t _dsti;
            W _w;

            Edge(size_t srci, size_t dsti, const W& w)
                    :_srci(srci)
                    , _dsti(dsti)
                    , _w(w)
            {}

            bool operator>(const Edge& e) const
            {
                //比较权值的大小，重载我们的>运算符
                return _w > e._w;
            }

        };

        void AddEdge(const V& src, const V& dst, const W& w)
        {
            size_t srci = GetVertexIndex(src);
            size_t dsti = GetVertexIndex(dst);
            _AddEdge(srci, dsti, w);
        }

        void _AddEdge(size_t srci, size_t dsti, const W& w)
        {
            _matrix[srci][dsti] = w;
            // 无向图
            if (Direction == false)
            {
                _matrix[dsti][srci] = w;
            }
        }

        W Kruskal(Self& minTree)
        {
            size_t n = _vertex.size();

            //创建我们的最小生成树
            minTree._vertex = _vertex;
            minTree._indexmap = _indexmap;
            //初始化我们最小生成树的矩阵
            minTree._matrix.resize(n);
            for (size_t i = 0; i < n; ++i)
            {
                minTree._matrix[i].resize(n, MAX_W);
            }

            //用优先级队列，这里我们需要让小的优先级高，也就是我们需要传入greater
            priority_queue<Edge, vector<Edge>, greater<Edge>> minque;
            for (size_t i = 0; i < n; ++i)
            {
                for (size_t j = 0; j < n; ++j)
                {
                    //将所有的边都放入优先级队列中
                    //i<j是为了避免重复添加
                    if (i < j && _matrix[i][j] != MAX_W)
                    {
                        minque.push(Edge(i, j, _matrix[i][j]));
                    }
                }
            }

            // 选出n-1条边
            int size = 0;
            //总的权值
            W totalW = W();
            //创建一个并查集，并查集代码参考我们上面的博客链接
            UnionFindSet ufs(n);
            while (!minque.empty())
            {
                Edge min = minque.top();
                minque.pop();

                //如果当前新增的边的两个顶点不在同一个集合中，也就是不相连的话，我们就可以添加这条边
                if (!ufs.InSet(min._srci, min._dsti))
                {
                    cout << _vertex[min._srci] << "->" << _vertex[min._dsti] <<":"<<min._w << endl;
                    //往我们的最小生成树中添加这条边
                    minTree._AddEdge(min._srci, min._dsti, min._w);
                    //将这条边添加到我们的并查集当中
                    ufs.Union(min._srci, min._dsti);
                    ++size;
                    totalW += min._w;
                }
                else
                {
                    cout << "构成环：";
                    cout << _vertex[min._srci] << "->" << _vertex[min._dsti] << ":" << min._w << endl;
                }
            }

            //找到了最小生成树
            if (size == n - 1)
            {
                return totalW;
            }
            //如果没有找到就返回权值
            else
            {
                return W();
            }
        }

```

测试代码
```c++
void TestGraphMinTree()
    {
        const char* str = "abcdefghi";
        Graph<char, int> g(str, strlen(str));
        g.AddEdge('a', 'b', 4);
        g.AddEdge('a', 'h', 8);
        //g.AddEdge('a', 'h', 9);
        g.AddEdge('b', 'c', 8);
        g.AddEdge('b', 'h', 11);
        g.AddEdge('c', 'i', 2);
        g.AddEdge('c', 'f', 4);
        g.AddEdge('c', 'd', 7);
        g.AddEdge('d', 'f', 14);
        g.AddEdge('d', 'e', 9);
        g.AddEdge('e', 'f', 10);
        g.AddEdge('f', 'g', 2);
        g.AddEdge('g', 'h', 1);
        g.AddEdge('g', 'i', 6);
        g.AddEdge('h', 'i', 7);

        Graph<char, int> kminTree;
        cout << "Kruskal:" << g.Kruskal(kminTree) << endl;
        kminTree.Print();
    }

```

#### Prim算法
```c++
//我们要选择一个起点
        W Prim(Self& minTree, const W& src)
        {
            //获取这个起点的下标
            size_t srci = GetVertexIndex(src);
            size_t n = _vertex.size();

            minTree._vertex = _vertex;
            minTree._indexmap = _indexmap;
            minTree._matrix.resize(n);
            for (size_t i = 0; i < n; ++i)
            {
                minTree._matrix[i].resize(n, MAX_W);
            }
            //同两个数组，分别表示已经被最小生成树选中的结点和没有被最小生成树选中的结点
            vector<bool> X(n, false);
            vector<bool> Y(n, true);
            X[srci] = true;
            Y[srci] = false;

            // 从X->Y集合中连接的边里面选出最小的边
            priority_queue<Edge, vector<Edge>, greater<Edge>> minq;
            // 先把srci连接的边添加到队列中
            for (size_t i = 0; i < n; ++i)
            {
                if (_matrix[srci][i] != MAX_W)
                {
                    //分别将起始点，指向的最终点和权值构成的边放入队列中
                    minq.push(Edge(srci, i, _matrix[srci][i]));
                }
            }

            size_t size = 0;
            W totalW = W();
            while (!minq.empty())
            {
                Edge min = minq.top();
                minq.pop();

                // 最小边的目标点也在X集合，则构成环
                if (X[min._dsti])
                {
                    //cout << "构成环:";
                    //cout << _vertexs[min._srci] << "->" << _vertexs[min._dsti] << ":" << min._w << endl;
                }
                else
                {
                    //将这条边添加到我们的最小生成树当中
                    minTree._AddEdge(min._srci, min._dsti, min._w);
                    //cout << _vertexs[min._srci] << "->" << _vertexs[min._dsti] << ":" << min._w << endl;
                    //X中对应的点将其标记成true代表已经加入了x集合
                    X[min._dsti]= true;
                    //Y代表的是还没有被连接的点，所以我们将我们这个已经被连接的点的位置标记成false
                    Y[min._dsti] = false;
                    ++size;
                    totalW += min._w;
                    //如果选出了了n-1条边，那么我们选边就已经结束了
                    if (size == n - 1)
                        break;

                    for (size_t i = 0; i < n; ++i)
                    {
                        //将当前边的终点作为我们挑选下一条边的起点，并且这条起点的终点不能在我们的X集合中
                        //然后将这些点重新放入我们的队列中
                        if (_matrix[min._dsti][i] != MAX_W && Y[i])
                        {
                            minq.push(Edge(min._dsti, i, _matrix[min._dsti][i]));
                        }
                    }
                }
            }
            //选到了n-1条边就返回总的权重
            if (size == n - 1)
            {
                return totalW;
            }
            else
            {
                return W();
            }
        }

```

测试代码
```c++
void TestGraphMinTree2()
    {
        const char* str = "abcdefghi";
        Graph<char, int> g(str, strlen(str));
        g.AddEdge('a', 'b', 4);
        g.AddEdge('a', 'h', 8);
        //g.AddEdge('a', 'h', 9);
        g.AddEdge('b', 'c', 8);
        g.AddEdge('b', 'h', 11);
        g.AddEdge('c', 'i', 2);
        g.AddEdge('c', 'f', 4);
        g.AddEdge('c', 'd', 7);
        g.AddEdge('d', 'f', 14);
        g.AddEdge('d', 'e', 9);
        g.AddEdge('e', 'f', 10);
        g.AddEdge('f', 'g', 2);
        g.AddEdge('g', 'h', 1);
        g.AddEdge('g', 'i', 6);
        g.AddEdge('h', 'i', 7);

        Graph<char, int> pminTree;
        cout << "Prim:" << g.Prim(pminTree, 'a') << endl;
        pminTree.Print();
        cout << endl;

    }

```

---

### 最短路径

#### Dijkstra算法

```c++
//打印最短路径
        void PrintShortPath(const V& src, const vector<W>& dist, const vector<int>& pPath)
        {
            //获取目标点的对应的索引
            size_t srci = GetVertexIndex(src);
            //获取一共的点的个数
            size_t n = _vertex.size();
            for (size_t i = 0; i < n; ++i)
            {
                //如果i不是我们当前的源点，也就是需要排除自己走到自己的情况
                if (i != srci)
                {
                    // 找出i顶点的路径
                    vector<int> path;
                    size_t parenti = i;
                    //如果父节点不是我们的源，我们就不断向前查找，并且将我们的路径记录到我们的path当中
                    while (parenti != srci)
                    {
                        path.push_back(parenti);
                        parenti = pPath[parenti];
                    }
                    path.push_back(srci);
                    //由于我们是从后向前寻找的，所以我们需要将我们的vector逆置一下
                    reverse(path.begin(), path.end());

                    for (auto index : path)
                    {
                        cout << _vertex[index] << "->";
                    }
                    cout << dist[i] << endl;
                }
            }
        }

        //传入源点，
        // 传入存储源点到其他各个点的最短路径的权值和容器（例：点s到syzx的路径）
        //传入每个节点的父路径，也就是从我们的源节点到我们每一个节点的最短路径的前一个节点的下标
        void Dijkstra(const V& src, vector<W>& dist, vector<int>& pPath)
        {
            //源点的下标
            size_t srci = GetVertexIndex(src);
            //节点的数量
            size_t n = _vertex.size();
            //将所有的路径初始化为无穷大
            dist.resize(n, MAX_W);
            //将路径全部都初始化成-1，也就是没有前一个结点（我们结点的下标从0开始）
            pPath.resize(n, -1);
            //自己结点到自己的距离就是0
            dist[srci] = 0;
            //自己到自己的最短路径的前一个节点就是自己，所以前一个节点的下标也是自己
            pPath[srci] = srci;

            // 标记已经确定最短路径的顶点集合，初始全部都是false，也就是全部都没有被确定下来
            vector<bool> S(n, false);

            for (size_t j = 0; j < n; ++j)
            {
                // 选最短路径顶点且不在S更新其他路径
                //最小的点为u，初始化为0
                int u = 0;
                //记录到最小的点的权值
                W min = MAX_W;
                for (size_t i = 0; i < n; ++i)
                {
                    //这个点没有被选过，并且到这个点的权值比我们当前的最小值更小，我们就进行更新
                    if (S[i] == false && dist[i] < min)
                    {
                        //用u记录这个最近的点的编号
                        u = i;
                        min = dist[i];
                    }
                }
                //标记当前点已经被选中了
                S[u] = true;
                // 松弛更新u连接顶点v  srci->u + u->v <  srci->v  更新
                //确定u链接出去的所有点
                for (size_t v = 0; v < n; ++v)
                {
                    //如果v这个点没有被标记过，也就是我们这个点还没有被确定最短距离，并且从我们当前点u走到v的路径是存在的
                    //并且从u走到v的总权值的和比之前源点到v的权值更小，我们就更新我们从源点到我们的v的最小权值
                    if (S[v] == false && _matrix[u][v] != MAX_W
                        && dist[u] + _matrix[u][v] < dist[v])
                    {
                        //更新从源点到v的最小权值
                        dist[v] = dist[u] + _matrix[u][v];
                        //标记我们从源点到v的最小路径要走到v这一步的前一个节点需要走u
                        pPath[v] = u;
                    }
                }
            }
        }

```

测试代码
```c++
void TestGraphDijkstra()
    {
        const char* str = "syztx";
        Graph<char, int, INT_MAX, true> g(str, strlen(str));
        g.AddEdge('s', 't', 10);
        g.AddEdge('s', 'y', 5);
        g.AddEdge('y', 't', 3);
        g.AddEdge('y', 'x', 9);
        g.AddEdge('y', 'z', 2);
        g.AddEdge('z', 's', 7);
        g.AddEdge('z', 'x', 6);
        g.AddEdge('t', 'y', 2);
        g.AddEdge('t', 'x', 1);
        g.AddEdge('x', 'z', 4);

        vector<int> dist;
        vector<int> parentPath;
        g.Dijkstra('s', dist, parentPath);
        g.PrintShortPath('s', dist, parentPath);

    }

```

#### Bellman-Ford算法（贝尔曼福特算法）

```c++
// 时间复杂度：O(N^3) 空间复杂度：O（N）
        bool BellmanFord(const V& src, vector<W>& dist, vector<int>& pPath)
        {
            //获取我们点的总和数
            size_t n = _vertex.size();
            //获取我们源点的索引
            size_t srci = GetVertexIndex(src);

            // vector<W> dist,记录srci-其他顶点最短路径权值数组
            dist.resize(n, MAX_W);

            // vector<int> pPath 记录srci-其他顶点最短路径父顶点数组
            pPath.resize(n, -1);

            // 先更新srci->srci为缺省值
            dist[srci] = W();

            //cout << "更新边：i->j" << endl;


            // 总体最多更新n轮
            //从s->t最多经过n条边，否则就会变成回路。
            //每一条路径的更新都可能会影响别的路径
            for (size_t k = 0; k < n; ++k)
            {
                // i->j 更新松弛
                bool update = false;
                cout << "更新第:" << k << "轮" << endl;
                for (size_t i = 0; i < n; ++i)
                {
                    for (size_t j = 0; j < n; ++j)
                    {
                        // srci -> i + i ->j
                        //如果i->j边存在的话，并且srci -> i + i ->j比原来的距离更小，就更新该路径
                        if (_matrix[i][j] != MAX_W && dist[i] + _matrix[i][j] < dist[j])
                        {
                            //这一轮有发生更新
                            update = true;
                            cout << _vertex[i] << "->" << _vertex[j] << ":" << _matrix[i][j] << endl;
                            dist[j] = dist[i] + _matrix[i][j];
                            //记录当前点的前一个节点
                            pPath[j] = i;
                        }
                    }
                }

                // 如果这个轮次中没有更新出更短路径，那么后续轮次就不需要再走了
                if (update == false)
                {
                    break;
                }
            }


            // 还能更新就是带负权回路，具体的例子在下面
            for (size_t i = 0; i < n; ++i)
            {
                for (size_t j = 0; j < n; ++j)
                {
                    // srci -> i + i ->j
                    if (_matrix[i][j] != MAX_W && dist[i] + _matrix[i][j] < dist[j])
                    {
                        return false;
                    }
                }
            }

            return true;
        }

```

测试代码
```c++
void TestGraphBellmanFord()
    {
        	const char* str = "syztx";
            Graph<char, int, INT_MAX, true> g(str, strlen(str));
            g.AddEdge('s', 't', 6);
            g.AddEdge('s', 'y', 7);
            g.AddEdge('y', 'z', 9);
            g.AddEdge('y', 'x', -3);
            g.AddEdge('z', 's', 2);
            g.AddEdge('z', 'x', 7);
            g.AddEdge('t', 'x', 5);
            g.AddEdge('t', 'y', 8);
            g.AddEdge('t', 'z', -4);
            g.AddEdge('x', 't', -2);
            vector<int> dist;
            vector<int> parentPath;
            g.BellmanFord('s', dist, parentPath);
            g.PrintShortPath('s', dist, parentPath);


```

#### Floyd-Warshall算法（弗洛伊德算法）
```c++
void FloydWarshall(vector<vector<W>>& vvDist, vector<vector<int>>& vvpPath)
        {
            //获取一共有多少个点
            size_t n = _vertex.size();
            vvDist.resize(n);
            vvpPath.resize(n);

            // 初始化权值和路径矩阵
            for (size_t i = 0; i < n; ++i)
            {
                //设置成最大值，表示不相通
                vvDist[i].resize(n, MAX_W);
                //设置成-1表示没有父路径
                vvpPath[i].resize(n, -1);
            }

            // 直接相连的边更新一下
            for (size_t i = 0; i < n; ++i)
            {
                for (size_t j = 0; j < n; ++j)
                {
                    if (_matrix[i][j] != MAX_W)
                    {
                        vvDist[i][j] = _matrix[i][j];
                        //连接的上一个点
                        vvpPath[i][j] = i;
                    }
                    //自己跟自己相连的话，就更新成0
                    if (i == j)
                    {
                        vvDist[i][j] = W();
                    }
                }
            }
            //所有点都有可能成为别的路径的中间点
            // abcdef  a {} f ||  b {} c
            // 最短路径的更新i-> {其他顶点} ->j
            //这里的k就是遍历所有的点，假设i到j的路径经过k这个点会不会比不经过k更短。
            for (size_t k = 0; k < n; ++k)
            {
                for (size_t i = 0; i < n; ++i)
                {
                    for (size_t j = 0; j < n; ++j)
                    {
                        // k 作为的中间点尝试去更新i->j的路径
                        if (vvDist[i][k] != MAX_W && vvDist[k][j] != MAX_W
                        //如果经过k点我们的路径会变得更短
                            && vvDist[i][k] + vvDist[k][j] < vvDist[i][j])
                        {
                            //更新i,j
                            vvDist[i][j] = vvDist[i][k] + vvDist[k][j];

                            // 找跟j相连的上一个邻接顶点
                            // 如果k->j 直接相连，上一个点就是k，vvpPath[k][j]存就是k
                            // 如果k->j 没有直接相连，比如说中间还经过了别的点 k->...->x->j，vvpPath[k][j]存就是x
                            //vvpPath[i][j]= vvpPath[k][j]代表想要走到j这个点之前还要先想办法走到k这个点
                            vvpPath[i][j] = vvpPath[k][j];
                        }
                    }
                }

                // 打印权值和路径矩阵观察数据
                for (size_t i = 0; i < n; ++i)
                {
                    for (size_t j = 0; j < n; ++j)
                    {
                        if (vvDist[i][j] == MAX_W)
                        {
                            //cout << "*" << " ";
                            printf("%3c", '*');
                        }
                        else
                        {
                            //cout << vvDist[i][j] << " ";
                            printf("%3d", vvDist[i][j]);
                        }
                    }
                    cout << endl;
                }
                cout << endl;

                for (size_t i = 0; i < n; ++i)
                {
                    for (size_t j = 0; j < n; ++j)
                    {
                        //cout << vvParentPath[i][j] << " ";
                        printf("%3d", vvpPath[i][j]);
                    }
                    cout << endl;
                }
                cout << "=================================" << endl;
            }
        }

```

测试代码
```c++
void TestFloydWarShall()
    {
        const char* str = "12345";
        Graph<char, int, INT_MAX, true> g(str, strlen(str));
        g.AddEdge('1', '2', 3);
        g.AddEdge('1', '3', 8);
        g.AddEdge('1', '5', -4);
        g.AddEdge('2', '4', 1);
        g.AddEdge('2', '5', 7);
        g.AddEdge('3', '2', 4);
        g.AddEdge('4', '1', 2);
        g.AddEdge('4', '3', -5);
        g.AddEdge('5', '4', 6);
        vector<vector<int>> vvDist;
        vector<vector<int>> vvParentPath;
        g.FloydWarshall(vvDist, vvParentPath);

        // 打印任意两点之间的最短路径
        for (size_t i = 0; i < strlen(str); ++i)
        {
            g.PrintShortPath(str[i], vvDist[i], vvParentPath[i]);
            cout << endl;
        }
    }

```