---
layout: post
title: Capture Packet
date: 2020-07-08 23:01:00
categories:
- Developer Tools
tags:
- Capture Packet
- Open source library
- Tool
---

July 8, 2020 10:23 PM

<!--more-->
## Fiddler--The Web Debugging Proxy Tool Loved by Users
[DownLoad](https://www.telerik.com/fiddler)
Address: 127.0.0.1 Port: 8888

Log all HTTP(S) traffic between your computer and the Internet. Inspect traffic, set breakpoints and fiddle with request/response

## Microsoft Network Monitor 3.4 (archive)
[DownLoad](https://www.microsoft.com/en-us/download/details.aspx?id=4865)
Network Monitor 3.4 is the archive versioned tool for network traffic capture and protocol analysis.

## Microsoft Message Analyzer(MMA)
Microsoft Message Analyzer is a tool for capturing, displaying, and analyzing protocol messaging traffic, events, and other system or application messages in network troubleshooting and other diagnostic scenarios. Message Analyzer also enables you to load, aggregate, and analyze data from log and saved trace files. 

## NetSpeedMonitor
[DownLoad](https://netspeedmonitor64.en.softonic.com/)
NetSpeedMonitor is a free utility tool using which you can observe the speed of your internet connection. With its help, you can track network issues, analyze the amount of transferred data, and view monthly traffic statistics. 

## Tcpdump
[HomePage](http://www.tcpdump.org/index.html)
- a powerful command-line packet analyzer; and libpcap, a portable C/C++ library for network traffic capture

[Manpage](http://www.tcpdump.org/manpages/tcpdump.1.html)

[抓包总结](https://www.cnblogs.com/chenpingzhao/p/9108570.html)

## WinPcap
[HomePage](https://www.winpcap.org/)
For many years, WinPcap has been recognized as the industry-standard tool for link-layer network access in Windows environments, allowing applications to capture and transmit network packets bypassing the protocol stack, and including kernel-level packet filtering, a network statistics engine and support for remote packet capture.

WinPcap consists of a driver that extends the operating system to provide low-level network access and a library that is used to easily access low-level network layers. This library also contains the Windows version of the well-known libpcap Unix API.

Thanks to its set of features, WinPcap has been the packet capture and filtering engine for many open source and commercial network tools, including protocol analyzers, network monitors, network intrusion detection systems, sniffers, traffic generators and network testers. Some of these networking tools, like Wireshark, Nmap, Snort, and ntop are known and used throughout the networking community.

Winpcap.org is also the home of WinDump, the Windows version of the popular tcpdump tool. WinDump can be used to watch, diagnose and save to disk network traffic according to various complex rules.

## Npcap
[HomePage](https://nmap.org/npcap/)

[Other Introduce](https://blog.csdn.net/hsluoyc/article/details/46483151)
- Npcap源代码采用GitHub托管，其Repository地址为：https://github.com/nmap/npcap

Npcap is the Nmap Project's packet sniffing (and sending) library for Windows. It is based on the discontinued WinPcap library, but with improved speed, portability, security, and efficiency. In particular, Npcap offers:

- WinPcap for Windows 10: Npcap works on Windows 7 and later by making use of the new NDIS 6 Light-Weight Filter (LWF) API. It's faster than the deprecated NDIS 5 API, which Microsoft could remove at any time. Also, the driver is signed with our EV certificate and countersigned by Microsoft, so it works even with the stricter driver signing requirements in Windows 10 1607.
- Extra Security: Npcap can (optionally) be restricted so that only Administrators can sniff packets. If a non-Admin user tries to utilize Npcap through software such as Nmap or Wireshark, the user will have to pass a User Account Control (UAC) dialog to utilize the driver. This is conceptually similar to UNIX, where root access is generally required to capture packets. We've also enabled the Windows ASLR and DEP security features and signed the driver, DLLs, and executables to prevent tampering.
- Loopback Packet Capture: Npcap is able to sniff loopback packets (transmissions between services on the same machine) by using the Windows Filtering Platform (WFP). After installation, Npcap will create an adapter named Npcap Loopback Adapter for you. If you are a Wireshark user, choose this adapter to capture, you will see all loopback traffic the same way as other non-loopback adapters. Try it by typing in commands like “ping 127.0.0.1” (IPv4) or “ping ::1” (IPv6).
- Loopback Packet Injection: Npcap is also able to send loopback packets using the Winsock Kernel (WSK) technique. User-level software such as Nping can just send the packets out using Npcap Loopback Adapter just like any other adapter. Npcap then does the magic of removing the packet's Ethernet header and injecting the payload into the Windows TCP/IP stack.
- Libpcap API: Npcap uses the excellent Libpcap library, enabling Windows applications to use a portable packet capturing API that is also supported on Linux and Mac OS X. While WinPcap was based on LibPcap 1.0.0 from 2009, Npcap includes the latest Libpcap release along with improvements that we also contribute back upstream to Libpcap.
- WinPcap compatibility: For applications that don't yet make use of Npcap's advanced features, Npcap can be installed in “WinPcap Compatible Mode.” This will replace any existing WinPcap installation. If compatibility mode is not selected, Npcap can coexist alongside WinPcap; applications which only know about WinPcap will continue using that, while other applications can choose to use the newer and faster Npcap driver instead.

## Wireshark
