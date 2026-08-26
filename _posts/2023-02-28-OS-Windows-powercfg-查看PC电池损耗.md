---
layout: post
title: "OS-Windows-powercfg 查看PC电池损耗"
date: 2023-02-28 22:21:00
categories: ["OS"]
tags: ["OS", "Tool", "Windows"]
---

windows系统相关命令 `powercfg`

<!--more-->
`powercfg /?` 可以查看命令提示，

`powercfg /batteryreport` 命令生成电池使用情况报告，
- Design capacity(电池设计容量);
- Full charge capacity(现在电池充满的容量);

## POWERCFG 命令列表
```

POWERCFG /命令 [参数]

描述:
  使用户可以控制本地系统上的电源设置。

  有关命令和选项的详细信息，请运行 "POWERCFG /? <COMMAND>"

命令列表:
  /LIST、/L          列出所有电源方案。

  /QUERY、/Q         显示电源方案的内容。

  /CHANGE、/X        修改当前电源方案中的设置值。

  /CHANGENAME        修改电源方案的名称和描述。

  /DUPLICATESCHEME   复制电源方案。

  /DELETE, /D        删除电源方案。

  /DELETESETTING     删除电源设置。

  /SETACTIVE, /S     使系统上的电源方案处于活动状态。

  /GETACTIVESCHEME   检索当前活动的电源方案。

  /SETACVALUEINDEX   如果系统使用交流电源供电，
                     则设置与电源设置相关联的值。

  /SETDCVALUEINDEX   如果系统使用直流电源供电，
                     则设置与电源设置相关联的值。

  /IMPORT            从文件中导入所有电源设置。

  /EXPORT            将电源方案导出到文件。

  /ALIASES           显示所有别名及其相应的 GUID。

  /GETSECURITYDESCRIPTOR
                     获取与指定的
                     电源设置、电源方案或操作相关联的安全描述符。

  /SETSECURITYDESCRIPTOR
                     设置与
                     电源设置、电源方案或操作相关联的安全描述符。

  /HIBERNATE、/H     启用或禁用休眠功能。

  /AVAILABLESLEEPSTATES、/A
                     报告系统上可用的睡眠状态。

  /DEVICEQUERY      返回符合指定条件的设备列表。

  /DEVICEENABLEWAKE  使设备从睡眠状态唤醒系统。

  /DEVICEDISABLEWAKE 禁止设备从任何睡眠
                     状态唤醒系统。

  /LASTWAKE          报告有关从上次睡眠转换中
                     唤醒系统的信息。

  /WAKETIMERS        枚举活动的唤醒计时器。

  /REQUESTS          枚举应用程序和驱动程序的电源请求。

  /REQUESTSOVERRIDE  为特定进程、
                     服务或驱动程序设置电源请求替代。

  /ENERGY            分析系统中常见的能量效率和
                     电池使用时间问题。

  /BATTERYREPORT     生成电池使用情况的报告。

  /SLEEPSTUDY        生成系统电源转换的诊断报告。

  /SRUMUTIL          从系统资源使用状况监视器(SRUM)转储能量
                     估算数据。

  /SYSTEMSLEEPDIAGNOSTICS
                     生成系统睡眠转换的诊断报告。

  /SYSTEMPOWERREPORT 生成系统电源转换的诊断报告。

  /POWERTHROTTLING 为应用程序控制电源节流。

```

## 默认报告 battery-report.html
默认报告 battery-report.html

```html
<!DOCTYPE html>
<!-- saved from url=(0016)http://localhost -->
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:ms="urn:schemas-microsoft-com:xslt" xmlns:bat="http://schemas.microsoft.com/battery/2012" xmlns:js="http://microsoft.com/kernel"><head><meta http-equiv="X-UA-Compatible" content="IE=edge"/><meta name="ReportUtcOffset" content="+8:00"/><title>Battery report</title><style type="text/css">

      body {

          font-family: Segoe UI Light;

          letter-spacing: 0.02em;

          background-color: #181818;

          color: #F0F0F0;

          margin-left: 5.5em;

      }



      h1 {

          color: #11D8E8;

          font-size: 42pt;

      }



      h2 {

          font-size: 15pt;

          color: #11EEF4;

          margin-top: 4em;

          margin-bottom: 0em;

          letter-spacing: 0.08em;

      }



      td {

          padding-left: 0.3em;

          padding-right: 0.3em;

      }



      .nobatts {

          font-family: Segoe UI Semibold;

          background: #272727;

          color: #ACAC60;

          font-size: 13pt;

          padding-left:0.4em;

          padding-right:0.4em;

          padding-top:0.3em;

          padding-bottom:0.3em;

      }



      .explanation {

          color: #777777;

          font-size: 12pt;

          margin-bottom: 1em;

      }



      .explanation2 {

          color: #777777;

          font-size: 12pt;

          margin-bottom: 0.1em;

      }



      table {

          border-width: 0;

          table-layout: fixed;

          font-family: Segoe UI Light;

          letter-spacing: 0.02em;

          background-color: #181818;

          color: #f0f0f0;

      }



      .even { background: #272727; }

      .odd { background: #1E1E1E; }

      .even.suspend { background: #1A1A28; }

      .odd.suspend { background: #1A1A2C; }



      thead {

          font-family: Segoe UI Semibold;

          font-size: 85%;

          color: #BCBCBC;

      }



      text {

          font-size: 12pt;

          font-family: Segoe UI Light;

          fill: #11EEF4;

      }



      .centered { text-align: center; }



      .label {

          font-family: Segoe UI Semibold;

          font-size: 85%;

          color: #BCBCBC;

      }



      .dc.even { background: #40182C; }

      .dc.odd { background: #30141F; }



      td.colBreak {

          padding: 0;

          width: 0.15em;

      }



      td.state { text-align: center; }



      td.hms {

          font-family: Segoe UI Symbol;

          text-align: right;

          padding-right: 3.4em;

      }



      td.dateTime { font-family: Segoe UI Symbol; }

      td.nullValue { text-align: center; }



      td.percent {

          font-family: Segoe UI Symbol;

          text-align: right;

          padding-right: 2.5em;

      }



      col:first-child { width: 13em; }

      col.col2 { width: 10.4em; }

      col.percent { width: 7.5em; }



      td.mw {

          text-align: right;

          padding-right: 2.5em;

      }



      td.acdc { text-align: center; }



      span.date {

          display: inline-block;

          width: 5.5em;

      }



      span.time {

          text-align: right;

          width: 4.2em;

          display: inline-block;

      }



      text { font-family: Segoe UI Symbol; }



      .noncontigbreak {

          height: 0.3em;

          background-color: #1A1A28;

      }

    </style><script type="text/javascript">

    // Formats a number using the current locale (to handle the 1000's separator).

    // The result is rounded so no decimal point is shown.

    function numberToLocaleString(value) {

        var localeString = Math.round(parseFloat(value + '')).toLocaleString();

        return localeString.substring(0, localeString.indexOf('.'));

    }



    function padLeft(number, length) {

        var str = '' + number;

        while (str.length < length) {

            str = '0' + str;

        }



        return str;

    }



    // Returns the number of milliseconds between 2 date-times represented as strings.

    function msBetween(startTime, endTime) {

        return startTime > endTime

               ? msBetween(endTime, startTime)

               : parseDateTime(endTime) - parseDateTime(startTime);

    }



    var dateFormat = /(\d{4})-(\d{2})-(\d{2})[T](\d{2}):(\d{2}):(\d{2})/



    // Parses a date-time string and returns a Date (i.e. number of milliseconds)

    function parseDateTime(value) {

        if (!value) {

            return 0;

        }



        var match = dateFormat.exec(value)

        if (!match) {

            return 0;

        }



        return Date.parse(match[1] + '/' + match[2] + '/' +

                          match[3] + ' ' + match[4] + ':' +

                          match[5] + ':' + match[6])

    }



    // Parses just the date portion of a date-time string and returns a Date

    // (i.e. number of milliseconds)

    function parseDate(value) {

        if (!value) {

            return 0;

        }



        var match = dateFormat.exec(value)

        if (!match) {

            return 0;

        }



        return Date.parse(match[1] + '/' + match[2] + '/' + match[3])

    }



    var durationFormat = /P((\d+)D)?T((\d+)H)?((\d+)M)?(\d+)S/



    // Convert a string of the form P10DT1H15M40S to a count of milliseconds

    function parseDurationToMs(value) {

        var match = durationFormat.exec(value)

        if (!match) {

            return 0

        }



        var days = parseInt(match[2] || '0');

        var hrs = parseInt(match[4] || '0');

        var mins = parseInt(match[6] || '0');

        var secs = parseInt(match[7] || '0');

        return ((((((days * 24) + hrs) * 60) + mins) * 60) +  secs) * 1000;

    }



    // Converts milliseconds to days

    function msToDays(ms) {

        return (ms / 1000 / 60 / 60 / 24);

    }



    function daysToMs(days) {

        return (days * 24 * 60 * 60 * 1000);

    }



    // Formats a number of milliseconds as h:mm:ss

    function formatDurationMs(value) {

        var ms = parseInt(value);

        var secs = ms / 1000;

        var mins = secs / 60;

        var hrs = Math.floor(mins / 60);

        mins = Math.floor(mins % 60);

        secs = Math.floor(secs % 60);

        return hrs + ':' + padLeft(mins,2) + ':' + padLeft(secs,2);

    }



    // Converts a millisecond timestamp to a day and month string

    // Note: dayOffset is forward from date.

    function dateToDayAndMonth(ms, dayOffset) {

        var adjustedDate = new Date(ms + (dayOffset * 24 * 60 * 60 * 1000));

        return padLeft(adjustedDate.getMonth() + 1, 2) + "-" +

               padLeft(adjustedDate.getDate(), 2);

    }



    // Takes a millisecond timestamp and returns a new millisecond timestamp

    // rounded down to the current day.

    function dateFloor(ms) {

        var dt = new Date(ms);

        return Date.parse(dt.getFullYear() + '/' + (dt.getMonth() + 1) + '/' + dt.getDate());

    }

    

    Timegraph = {

        axisTop: 9.5,

        axisRight: 24.5,

        axisBottom: 25.5,

        axisLeft: 25.5,

        ticks: 10,



        // Maximum number of 24 hour ticks for showing 12 and 6 hour ticks



        ticks12Hour: 8,

        ticks6Hour: 4,



        // Shading



        lineColor: "#B82830",

        shadingColor: "#4d1d35",



        precompute: function (graph) {

            var canvas = graph.canvas;

            var data = graph.data;

            var min = 0;

            var max = 0;



            graph.height = canvas.height - Timegraph.axisTop - Timegraph.axisBottom;

            graph.width = canvas.width - Timegraph.axisLeft - Timegraph.axisRight;

            for (var i = 0; i < data.length; i++) {

                data[i].t0 = parseDateTime(data[i].x0);

                data[i].t1 = parseDateTime(data[i].x1);



                if (i == 0) {

                    min = data[i].t0;

                    max = data[i].t1;

                }



                if (data[i].t0 < min) {

                    min = data[i].t0;

                }



                if (data[i].t1 > max) {

                    max = data[i].t1;

                }



                data[i].yy0 =

                    Timegraph.axisTop + graph.height - data[i].y0 * graph.height;



                data[i].yy1 =

                    Timegraph.axisTop + graph.height - data[i].y1 * graph.height;

            }



            if (graph.startTime != null) {

                graph.startMs = parseDateTime(graph.startTime);



            } else {

                graph.startMs = min;

            }



            graph.endMs = max;

            graph.durationMs = max - min;

        },



        drawFrame: function (graph) {

            var canvas = graph.canvas;

            var context = graph.context;



            graph.width =

                canvas.width - Timegraph.axisRight - Timegraph.axisLeft;



            graph.height =

                canvas.height - Timegraph.axisTop - Timegraph.axisBottom;



            context.beginPath();

            context.moveTo(Timegraph.axisLeft, Timegraph.axisTop);

            context.lineTo(Timegraph.axisLeft + graph.width,

                           Timegraph.axisTop);



            context.lineTo(Timegraph.axisLeft + graph.width,

                           Timegraph.axisTop + graph.height);



            context.lineTo(Timegraph.axisLeft,

                           Timegraph.axisTop + graph.height);



            context.lineTo(Timegraph.axisLeft, Timegraph.axisTop);

            context.strokeStyle = "#c0c0c0";

            context.stroke();

        },



        drawRange: function (graph) {

            var canvas = graph.canvas;

            var context = graph.context;



            context.font = "12pt Segoe UI";

            context.fillStyle = "#00b0f0";

            context.fillText("%", 0, Timegraph.axisTop + 5, Timegraph.axisLeft);



            var tickSpacing = graph.height / 10;

            var offset = Timegraph.axisTop + tickSpacing;

            var tickValue = 90;

            for (var i = 0; i < 9; i++) {

                context.beginPath();

                context.moveTo(Timegraph.axisLeft, offset);

                context.lineTo(Timegraph.axisLeft + graph.width,

                               offset);



                context.stroke();

                context.fillText(tickValue.toString(),

                                 0,

                                 offset + 5,

                                 Timegraph.axisLeft);



                offset += tickSpacing;

                tickValue -= 10;

            }

        },



        drawDomain: function (graph, start, end) {

            var canvas = graph.canvas;

            var context = graph.context;

            var data = graph.data;

            var duration = end - start;

            if ((end < start)) {

                return;

            }



            var startDay = dateFloor(start);

            var t0 = startDay;

            var t1 = dateFloor(end);

            var dayOffset = 0;

            if (start > t0) {

                t0 = t0 + daysToMs(1);

                dayOffset++;

            }



            if (t0 >= t1) {

                return;

            }



            var increment =

                Math.max(Math.floor((t1 - t0) / daysToMs(Timegraph.ticks)), 1);



            var incrementMs = daysToMs(increment);

            var spacing = (incrementMs / duration) * graph.width;

            var offset = (t0 - start) / duration;

            var ticksCount = Math.floor((t1 - t0) / incrementMs);

            for (offset = offset * graph.width + Timegraph.axisLeft;

                 offset < (graph.width + Timegraph.axisLeft);

                 offset += spacing) {



                context.beginPath();

                context.moveTo(offset, Timegraph.axisTop);

                context.lineTo(offset, Timegraph.axisTop + graph.height);

                context.stroke();

                context.fillText(dateToDayAndMonth(startDay, dayOffset),

                                 offset,

                                 Timegraph.axisTop + graph.height + 15,

                                 spacing);



                dayOffset += increment;

            }

        },



        plot: function (graph, start, end) {

            var canvas = graph.canvas;

            var context = graph.context

            var data = graph.data;



            if ((end < start)) {

                return;

            }



            var duration = end - start;

            Timegraph.drawDomain(graph, start, end);

            context.fillStyle = Timegraph.shadingColor;

            for (var i = 0; i < data.length - 1; i++) {

                if ((data[i].t0 < start) || (data[i].t0 > end) ||

                    (data[i].t1 > end)) {



                    continue;

                }



                var x1 = (data[i].t0 - start) / duration;

                x1 = x1 * graph.width + Timegraph.axisLeft;



                var x2 = (data[i].t1 - start) / duration;

                x2 = x2 * graph.width + Timegraph.axisLeft;



                context.globalAlpha = 0.3;

                context.fillRect(x1, Timegraph.axisTop, (x2 - x1), graph.height);

                context.globalAlpha = 1;

                context.beginPath();

                context.strokeStyle = Timegraph.lineColor;

                context.lineWidth = 1.5;

                context.moveTo(x1, data[i].yy0);

                context.lineTo(x2, data[i].yy1);

                context.stroke();

            }

        },



        draw: function (graph) {

            var canvas = document.getElementById(graph.element);

            if (canvas == null) {

                return;

            }



            var context = canvas.getContext('2d');

            if (context == null) {

                return;

            }



            graph.width = 0;

            graph.height = 0;

            graph.context = context;

            graph.canvas = canvas;



            Timegraph.precompute(graph);

            Timegraph.drawFrame(graph);

            Timegraph.drawRange(graph);

            Timegraph.plot(graph, graph.startMs, graph.endMs);

        }

    };

    

    drainGraphData = [

    { x0: "2023-02-27T16:06:00", x1: "2023-02-27T16:57:59", y0: 1, y1: 0.9830860534124629 }, 

{ x0: "2023-02-27T16:57:59", x1: "2023-02-27T16:59:08", y0: 0.9830860534124629, y1: 0.9688427299703264 }, 

{ x0: "2023-02-27T16:59:08", x1: "2023-02-27T17:01:42", y0: 0.9688427299703264, y1: 0.9456973293768546 }, 

{ x0: "2023-02-27T17:01:42", x1: "2023-02-27T17:02:43", y0: 0.9456973293768546, y1: 0.9367952522255193 }, 

{ x0: "2023-02-28T20:42:28", x1: "2023-02-28T21:25:57", y0: 1, y1: 0.9934718100890207 }, 

{ x0: "2023-02-28T21:25:57", x1: "2023-02-28T21:29:31", y0: 0.9934718100890207, y1: 0.9341246290801187 }, 

{ x0: "2023-02-28T21:29:31", x1: "2023-02-28T21:30:21", y0: 0.9341246290801187, y1: 0.9204747774480713 }, 

{ x0: "2023-02-28T21:30:21", x1: "2023-02-28T21:30:58", y0: 0.9204747774480713, y1: 0.9115727002967359 }, 

{ x0: "2023-02-28T21:30:58", x1: "2023-02-28T21:31:31", y0: 0.9115727002967359, y1: 0.901186943620178 }, 

{ x0: "2023-02-28T21:31:31", x1: "2023-02-28T21:32:01", y0: 0.901186943620178, y1: 0.8943620178041542 }, 

{ x0: "2023-02-28T21:32:01", x1: "2023-02-28T21:32:37", y0: 0.8943620178041542, y1: 0.8839762611275964 }, 

{ x0: "2023-02-28T21:32:37", x1: "2023-02-28T21:33:20", y0: 0.8839762611275964, y1: 0.871513353115727 }, 

{ x0: "2023-02-28T21:33:20", x1: "2023-02-28T21:34:01", y0: 0.871513353115727, y1: 0.8608308605341246 }, 

{ x0: "2023-02-28T21:34:01", x1: "2023-02-28T21:34:23", y0: 0.8608308605341246, y1: 0.8540059347181009 }, 

{ x0: "2023-02-28T21:34:23", x1: "2023-02-28T21:35:21", y0: 0.8540059347181009, y1: 0.8382789317507419 }, 

{ x0: "2023-02-28T21:35:21", x1: "2023-02-28T21:35:41", y0: 0.8382789317507419, y1: 0.8332344213649852 }, 

{ x0: "2023-02-28T21:35:41", x1: "2023-02-28T21:36:24", y0: 0.8332344213649852, y1: 0.8210682492581602 }, 

{ x0: "2023-02-28T21:36:24", x1: "2023-02-28T21:37:00", y0: 0.8210682492581602, y1: 0.8103857566765579 }, 

{ x0: "2023-02-28T21:37:00", x1: "2023-02-28T21:37:31", y0: 0.8103857566765579, y1: 0.801780415430267 }, 

{ x0: "2023-02-28T21:37:31", x1: "2023-02-28T21:38:03", y0: 0.801780415430267, y1: 0.7925816023738872 }, 

{ x0: "2023-02-28T21:38:03", x1: "2023-02-28T21:38:40", y0: 0.7925816023738872, y1: 0.7818991097922848 }, 

{ x0: "2023-02-28T21:38:40", x1: "2023-02-28T21:39:24", y0: 0.7818991097922848, y1: 0.7712166172106825 }, 

{ x0: "2023-02-28T21:39:24", x1: "2023-02-28T21:40:04", y0: 0.7712166172106825, y1: 0.758753709198813 }, 

{ x0: "2023-02-28T21:40:04", x1: "2023-02-28T21:40:26", y0: 0.758753709198813, y1: 0.7534124629080119 }, 

{ x0: "2023-02-28T21:40:26", x1: "2023-02-28T21:41:02", y0: 0.7534124629080119, y1: 0.7427299703264095 }, 

{ x0: "2023-02-28T21:41:02", x1: "2023-02-28T21:41:32", y0: 0.7427299703264095, y1: 0.7335311572700297 }, 

{ x0: "2023-02-28T21:41:32", x1: "2023-02-28T21:42:05", y0: 0.7335311572700297, y1: 0.7246290801186943 }, 

{ x0: "2023-02-28T21:42:05", x1: "2023-02-28T21:42:41", y0: 0.7246290801186943, y1: 0.713946587537092 }, 

{ x0: "2023-02-28T21:42:41", x1: "2023-02-28T21:43:24", y0: 0.713946587537092, y1: 0.702967359050445 }, 

{ x0: "2023-02-28T21:43:24", x1: "2023-02-28T21:44:05", y0: 0.702967359050445, y1: 0.6899109792284866 }, 

{ x0: "2023-02-28T21:44:05", x1: "2023-02-28T21:44:26", y0: 0.6899109792284866, y1: 0.684272997032641 }, 

{ x0: "2023-02-28T21:44:26", x1: "2023-02-28T21:45:03", y0: 0.684272997032641, y1: 0.6732937685459941 }, 

{ x0: "2023-02-28T21:45:03", x1: "2023-02-28T21:45:31", y0: 0.6732937685459941, y1: 0.6640949554896143 }, 

{ x0: "2023-02-28T21:45:31", x1: "2023-02-28T21:46:26", y0: 0.6640949554896143, y1: 0.6501483679525223 }, 

{ x0: "2023-02-28T21:46:26", x1: "2023-02-28T21:47:03", y0: 0.6501483679525223, y1: 0.6397626112759643 }, 

{ x0: "2023-02-28T21:47:03", x1: "2023-02-28T21:47:25", y0: 0.6397626112759643, y1: 0.6323442136498516 }, 

{ x0: "2023-02-28T21:47:25", x1: "2023-02-28T21:48:05", y0: 0.6323442136498516, y1: 0.6228486646884273 }, 

{ x0: "2023-02-28T21:48:05", x1: "2023-02-28T21:49:04", y0: 0.6228486646884273, y1: 0.6136498516320474 }, 

{ x0: "2023-02-28T21:49:04", x1: "2023-02-28T21:50:06", y0: 0.6136498516320474, y1: 0.6041543026706232 }, 

{ x0: "2023-02-28T21:50:06", x1: "2023-02-28T21:51:25", y0: 0.6041543026706232, y1: 0.5899109792284867 }, 

{ x0: "2023-02-28T21:51:25", x1: "2023-02-28T21:51:45", y0: 0.5899109792284867, y1: 0.5845697329376854 }, 

{ x0: "2023-02-28T21:51:45", x1: "2023-02-28T21:52:27", y0: 0.5845697329376854, y1: 0.5735905044510385 }, 

{ x0: "2023-02-28T21:52:27", x1: "2023-02-28T21:53:04", y0: 0.5735905044510385, y1: 0.5632047477744807 }, 

{ x0: "2023-02-28T21:53:04", x1: "2023-02-28T21:53:45", y0: 0.5632047477744807, y1: 0.5531157270029674 }, 

{ x0: "2023-02-28T21:53:45", x1: "2023-02-28T21:54:07", y0: 0.5531157270029674, y1: 0.3062314540059347 }, 

{ x0: "2023-02-28T21:54:07", x1: "2023-02-28T21:54:28", y0: 0.3062314540059347, y1: 0.29910979228486645 }, 

{ x0: "2023-02-28T21:54:28", x1: "2023-02-28T21:55:05", y0: 0.29910979228486645, y1: 0.29020771513353116 }, 



    ];

    

    function main() {

        Timegraph.draw({

            element: "drain-graph",

            data: drainGraphData,

            startTime: "2023-02-25T22:00:36",

            endTime: "2023-02-28T22:00:39",

        });

    }



    if (window.addEventListener != null) {

        window.addEventListener("load", main, false);



    } else if (window.attachEvent != null) {

        window.attachEvent("onload", main);

    }

    </script></head><body><h1>

      Battery report

    </h1><table style="margin-bottom: 6em;"><col/><tr><td class="label">

          COMPUTER NAME

        </td><td>W-PC</td></tr><tr><td class="label">

          SYSTEM PRODUCT NAME

        </td><td>TOSHIBA Satellite C805</td></tr><tr><td class="label">

          BIOS

        </td><td>6.50 12/27/2012</td></tr><tr><td class="label">

          OS BUILD

        </td><td>19041.1.amd64fre.vb_release.191206-1406</td></tr><tr><td class="label">

          PLATFORM ROLE

        </td><td>Mobile</td></tr><tr><td class="label">

          CONNECTED STANDBY

        </td><td>Not supported</td></tr><tr><td class="label">

          REPORT TIME

        </td><td class="dateTime"><span class="date">2023-02-28 </span><span class="time">22:00:39</span></td></tr></table><h2>

      Installed batteries

    </h2><div class="explanation">

      Information about each currently installed battery

    </div><table><colgroup><col style="width: 15em;"/><col style="width: 14em;"/></colgroup><thead><tr><td> </td><td>

                  BATTERY

                  1</td></tr></thead><tr><td><span class="label">NAME</span></td><td>PA5024U-1BRS</td></tr><tr><td><span class="label">MANUFACTURER</span></td><td>SANYO</td></tr><tr><td><span class="label">SERIAL NUMBER</span></td><td>

        -

      </td></tr><tr><td><span class="label">CHEMISTRY</span></td><td>LION</td></tr><tr><td><span class="label">DESIGN CAPACITY</span></td><td>4,400 mWh

      </td></tr><tr style="height:0.4em;"></tr><tr><td><span class="label">FULL CHARGE CAPACITY</span></td><td>3,370 mWh

      </td></tr><tr><td><span class="label">CYCLE COUNT</span></td><td>57</td></tr></table><h2>Recent usage</h2><div class="explanation">

      Power states over the last 3 days

    </div><table><colgroup><col/><col class="col2"/><col style="width: 4.2em;"/><col class="percent"/><col style="width: 11em;"/></colgroup><thead><tr><td>

            START TIME

          </td><td class="centered">

            STATE

          </td><td class="centered">

            SOURCE

          </td><td colspan="2" class="centered">

            CAPACITY REMAINING

          </td></tr></thead><tr class="even  1"><td class="dateTime"><span class="date">2023-02-25 </span><span class="time">22:27:00</span></td><td class="state">

        Active

      </td><td class="acdc">

        AC

      </td><td class="percent">100 %

        </td><td class="mw">3,370 mWh

        </td></tr><tr class="odd dc 2"><td class="dateTime"><span class="date">2023-02-27 </span><span class="time">16:57:59</span></td><td class="state">

        Active

      </td><td class="acdc">

        Battery

      </td><td class="percent">98 %

        </td><td class="mw">3,313 mWh

        </td></tr><tr class="even  3"><td class="dateTime"><span class="date"> </span><span class="time">17:02:51</span></td><td class="state">

        Active

      </td><td class="acdc">

        AC

      </td><td class="percent">94 %

        </td><td class="mw">3,151 mWh

        </td></tr><tr class="odd dc 4"><td class="dateTime"><span class="date">2023-02-28 </span><span class="time">21:25:57</span></td><td class="state">

        Active

      </td><td class="acdc">

        Battery

      </td><td class="percent">99 %

        </td><td class="mw">3,348 mWh

        </td></tr><tr class="even  5"><td class="dateTime"><span class="date"> </span><span class="time">21:55:39</span></td><td class="state">

        Active

      </td><td class="acdc">

        AC

      </td><td class="percent">6 %

        </td><td class="mw">206 mWh

        </td></tr><tr class="odd  6"><td class="dateTime"><span class="date"> </span><span class="time">22:00:36</span></td><td class="state">

        Report generated

      </td><td class="acdc">

        AC

      </td><td class="percent">10 %

        </td><td class="mw">326 mWh

        </td></tr></table><h2>Battery usage</h2><div class="explanation">

      Battery drains over the last 3 days

    </div><canvas id="drain-graph" width="864" height="400"></canvas><table><colgroup><col/><col class="col2"/><col style="width: 10em;"/><col class="percent"/><col style="width: 11em;"/></colgroup><thead><tr><td>

            START TIME

          </td><td class="centered">

            STATE

          </td><td class="centered">

            DURATION

          </td><td class="centered" colspan="2">

            ENERGY DRAINED

          </td></tr></thead><tr class="even dc 1"><td class="dateTime"><span class="date">2023-02-27 </span><span class="time">16:57:59</span></td><td class="state">

        Active

      </td><td class="hms">0:04:51</td><td class="percent">5 %

        </td><td class="mw">162 mWh

        </td></tr><tr class="noncontigbreak"><td colspan="5"> </td></tr><tr class="odd dc 2"><td class="dateTime"><span class="date">2023-02-28 </span><span class="time">21:25:57</span></td><td class="state">

        Active

      </td><td class="hms">0:29:41</td><td class="percent">93 %

        </td><td class="mw">3,142 mWh

        </td></tr></table><h2>

      Usage history

    </h2><div class="explanation2">

      History of system usage on AC and battery

    </div><table><colgroup><col/><col class="col2"/><col style="width: 10em;"/><col style=""/><col style="width: 10em;"/><col style="width: 10em;"/><col style=""/></colgroup><thead><tr><td> </td><td colspan="2" class="centered">

            BATTERY DURATION

          </td><td class="colBreak"> </td><td colspan="3" class="centered">

            AC DURATION

          </td></tr><tr><td>

            PERIOD

          </td><td class="centered">

            ACTIVE

          </td><td class="centered">

            CONNECTED STANDBY

          </td><td class="colBreak"> </td><td class="centered">

            ACTIVE

          </td><td class="centered">

            CONNECTED STANDBY

          </td></tr></thead><tr class="even  1"><td class="dateTime">2021-02-15

      - 2021-02-22</td><td class="hms">0:06:03</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">36:04:05</td><td class="nullValue">-</td></tr><tr class="odd  2"><td class="dateTime">2021-02-22

      - 2021-03-01</td><td class="hms">0:06:23</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">30:46:46</td><td class="nullValue">-</td></tr><tr class="even  3"><td class="dateTime">2021-03-01

      - 2021-03-08</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">29:08:09</td><td class="nullValue">-</td></tr><tr class="odd  4"><td class="dateTime">2021-03-08

      - 2021-03-15</td><td class="hms">0:28:25</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">30:51:15</td><td class="nullValue">-</td></tr><tr class="even  5"><td class="dateTime">2021-03-15

      - 2021-03-22</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">59:23:28</td><td class="nullValue">-</td></tr><tr class="odd  6"><td class="dateTime">2021-03-22

      - 2021-03-29</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">63:43:55</td><td class="nullValue">-</td></tr><tr class="even  7"><td class="dateTime">2021-03-29

      - 2021-04-05</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">59:39:19</td><td class="nullValue">-</td></tr><tr class="odd  8"><td class="dateTime">2021-04-05

      - 2021-04-12</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">38:14:59</td><td class="nullValue">-</td></tr><tr class="even  9"><td class="dateTime">2021-04-12

      - 2021-04-19</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">25:17:15</td><td class="nullValue">-</td></tr><tr class="odd  10"><td class="dateTime">2021-04-19

      - 2021-04-26</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">44:48:25</td><td class="nullValue">-</td></tr><tr class="even  11"><td class="dateTime">2021-04-26

      - 2021-05-03</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">13:39:12</td><td class="nullValue">-</td></tr><tr class="odd  12"><td class="dateTime">2021-05-03

      - 2021-05-10</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">15:49:28</td><td class="nullValue">-</td></tr><tr class="even  13"><td class="dateTime">2021-05-10

      - 2021-05-17</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">20:28:39</td><td class="nullValue">-</td></tr><tr class="odd  14"><td class="dateTime">2021-05-17

      - 2021-05-24</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">24:49:13</td><td class="nullValue">-</td></tr><tr class="even  15"><td class="dateTime">2021-05-24

      - 2021-05-31</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">18:57:18</td><td class="nullValue">-</td></tr><tr class="odd  16"><td class="dateTime">2021-05-31

      - 2021-06-07</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">24:14:17</td><td class="nullValue">-</td></tr><tr class="even  17"><td class="dateTime">2021-06-07

      - 2021-06-14</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">28:51:17</td><td class="nullValue">-</td></tr><tr class="odd  18"><td class="dateTime">2021-06-14

      - 2021-06-21</td><td class="hms">0:18:58</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">24:03:59</td><td class="nullValue">-</td></tr><tr class="even  19"><td class="dateTime">2021-06-21

      - 2021-06-28</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">27:50:32</td><td class="nullValue">-</td></tr><tr class="odd  20"><td class="dateTime">2021-06-28

      - 2021-07-05</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">38:46:39</td><td class="nullValue">-</td></tr><tr class="even  21"><td class="dateTime">2021-07-05

      - 2021-07-12</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">22:11:01</td><td class="nullValue">-</td></tr><tr class="odd  22"><td class="dateTime">2021-07-12

      - 2021-07-19</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">28:42:10</td><td class="nullValue">-</td></tr><tr class="even  23"><td class="dateTime">2021-07-19

      - 2021-07-26</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">15:46:19</td><td class="nullValue">-</td></tr><tr class="odd  24"><td class="dateTime">2021-07-26

      - 2021-08-02</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">22:51:11</td><td class="nullValue">-</td></tr><tr class="even  25"><td class="dateTime">2021-08-02

      - 2021-08-09</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">13:54:29</td><td class="nullValue">-</td></tr><tr class="odd  26"><td class="dateTime">2021-08-09

      - 2021-08-16</td><td class="hms">0:00:09</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">12:05:13</td><td class="nullValue">-</td></tr><tr class="even  27"><td class="dateTime">2021-08-16

      - 2021-08-23</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">17:29:43</td><td class="nullValue">-</td></tr><tr class="odd  28"><td class="dateTime">2021-08-23

      - 2021-08-30</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">11:49:16</td><td class="nullValue">-</td></tr><tr class="even  29"><td class="dateTime">2021-08-30

      - 2021-09-06</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">26:07:43</td><td class="nullValue">-</td></tr><tr class="odd  30"><td class="dateTime">2021-09-06

      - 2021-09-13</td><td class="hms">0:00:09</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">110:52:05</td><td class="nullValue">-</td></tr><tr class="even  31"><td class="dateTime">2021-09-13

      - 2021-09-20</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">29:46:25</td><td class="nullValue">-</td></tr><tr class="odd  32"><td class="dateTime">2021-09-20

      - 2021-09-27</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">38:15:54</td><td class="nullValue">-</td></tr><tr class="even  33"><td class="dateTime">2021-09-27

      - 2021-10-04</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">37:30:11</td><td class="nullValue">-</td></tr><tr class="odd  34"><td class="dateTime">2021-10-04

      - 2021-10-11</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">25:18:36</td><td class="nullValue">-</td></tr><tr class="even  35"><td class="dateTime">2021-10-11

      - 2021-10-18</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">19:54:29</td><td class="nullValue">-</td></tr><tr class="odd  36"><td class="dateTime">2021-10-18

      - 2021-10-25</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">21:40:23</td><td class="nullValue">-</td></tr><tr class="even  37"><td class="dateTime">2021-10-25

      - 2021-11-01</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">37:02:33</td><td class="nullValue">-</td></tr><tr class="odd  38"><td class="dateTime">2021-11-01

      - 2021-11-08</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">9:47:00</td><td class="nullValue">-</td></tr><tr class="even  39"><td class="dateTime">2021-11-08

      - 2021-11-15</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">21:00:29</td><td class="nullValue">-</td></tr><tr class="odd  40"><td class="dateTime">2021-11-15

      - 2021-11-22</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">39:54:39</td><td class="nullValue">-</td></tr><tr class="even  41"><td class="dateTime">2021-11-22

      - 2021-11-29</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">21:34:52</td><td class="nullValue">-</td></tr><tr class="odd  42"><td class="dateTime">2021-11-29

      - 2021-12-06</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">18:48:49</td><td class="nullValue">-</td></tr><tr class="even  43"><td class="dateTime">2021-12-06

      - 2021-12-13</td><td class="hms">0:00:14</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">195:06:59</td><td class="nullValue">-</td></tr><tr class="odd  44"><td class="dateTime">2021-12-13

      - 2021-12-20</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">21:33:39</td><td class="nullValue">-</td></tr><tr class="even  45"><td class="dateTime">2021-12-20

      - 2021-12-27</td><td class="hms">0:18:32</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">23:58:45</td><td class="nullValue">-</td></tr><tr class="odd  46"><td class="dateTime">2021-12-27

      - 2022-01-03</td><td class="hms">0:19:29</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">218:48:47</td><td class="nullValue">-</td></tr><tr class="even  47"><td class="dateTime">2022-01-03

      - 2022-01-10</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">70:09:49</td><td class="nullValue">-</td></tr><tr class="odd  48"><td class="dateTime">2022-01-10

      - 2022-01-24</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">118:31:52</td><td class="nullValue">-</td></tr><tr class="even  49"><td class="dateTime">2022-01-24

      - 2022-02-02</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">29:58:38</td><td class="nullValue">-</td></tr><tr class="odd  50"><td class="dateTime">2022-02-02

      - 2022-02-07</td><td class="hms">0:10:02</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">158:32:16</td><td class="nullValue">-</td></tr><tr class="even  51"><td class="dateTime">2022-02-07

      - 2022-02-14</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">2:17:34</td><td class="nullValue">-</td></tr><tr class="odd  52"><td class="dateTime">2022-02-14

      - 2022-02-21</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">4:55:48</td><td class="nullValue">-</td></tr><tr class="even  53"><td class="dateTime">2022-02-21

      - 2022-02-28</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">2:01:42</td><td class="nullValue">-</td></tr><tr class="odd  54"><td class="dateTime">2022-02-28

      - 2022-03-07</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">0:45:50</td><td class="nullValue">-</td></tr><tr class="even  55"><td class="dateTime">2022-03-07

      - 2022-03-15</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">16:27:54</td><td class="nullValue">-</td></tr><tr class="odd  56"><td class="dateTime">2022-03-15

      - 2022-03-28</td><td class="hms">0:02:14</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">24:22:15</td><td class="nullValue">-</td></tr><tr class="even  57"><td class="dateTime">2022-03-28

      - 2022-04-04</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">52:08:39</td><td class="nullValue">-</td></tr><tr class="odd  58"><td class="dateTime">2022-04-04

      - 2022-04-11</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">82:44:17</td><td class="nullValue">-</td></tr><tr class="even  59"><td class="dateTime">2022-04-11

      - 2022-04-18</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">101:57:35</td><td class="nullValue">-</td></tr><tr class="odd  60"><td class="dateTime">2022-04-18

      - 2022-04-25</td><td class="hms">0:26:23</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">82:38:06</td><td class="nullValue">-</td></tr><tr class="even  61"><td class="dateTime">2022-04-25

      - 2022-05-02</td><td class="hms">0:45:17</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">67:59:57</td><td class="nullValue">-</td></tr><tr class="odd  62"><td class="dateTime">2022-05-02

      - 2022-05-09</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">44:32:52</td><td class="nullValue">-</td></tr><tr class="even  63"><td class="dateTime">2022-05-09

      - 2022-05-16</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">62:41:06</td><td class="nullValue">-</td></tr><tr class="odd  64"><td class="dateTime">2022-05-16

      - 2022-05-23</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">55:19:48</td><td class="nullValue">-</td></tr><tr class="even  65"><td class="dateTime">2022-05-23

      - 2022-05-30</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">7:23:01</td><td class="nullValue">-</td></tr><tr class="odd  66"><td class="dateTime">2022-05-30

      - 2022-06-06</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">16:52:17</td><td class="nullValue">-</td></tr><tr class="even  67"><td class="dateTime">2022-06-06

      - 2022-06-16</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">7:51:56</td><td class="nullValue">-</td></tr><tr class="odd  68"><td class="dateTime">2022-06-16

      - 2022-06-21</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">0:25:57</td><td class="nullValue">-</td></tr><tr class="even  69"><td class="dateTime">2022-06-21

      - 2022-07-04</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">7:22:22</td><td class="nullValue">-</td></tr><tr class="odd  70"><td class="dateTime">2022-07-04

      - 2022-07-15</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">0:02:16</td><td class="nullValue">-</td></tr><tr class="even  71"><td class="dateTime">2022-07-15

      - 2022-07-18</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">0:58:58</td><td class="nullValue">-</td></tr><tr class="odd  72"><td class="dateTime">2022-07-18

      - 2022-07-25</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">3:01:09</td><td class="nullValue">-</td></tr><tr class="even  73"><td class="dateTime">2022-07-25

      - 2022-08-01</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">5:40:29</td><td class="nullValue">-</td></tr><tr class="odd  74"><td class="dateTime">2022-08-01

      - 2022-08-08</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">5:52:39</td><td class="nullValue">-</td></tr><tr class="even  75"><td class="dateTime">2022-08-08

      - 2022-08-22</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">23:23:44</td><td class="nullValue">-</td></tr><tr class="odd  76"><td class="dateTime">2022-08-22

      - 2022-09-01</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">22:23:17</td><td class="nullValue">-</td></tr><tr class="even  77"><td class="dateTime">2022-09-01

      - 2022-09-08</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">1:40:46</td><td class="nullValue">-</td></tr><tr class="odd  78"><td class="dateTime">2022-09-08

      - 2022-09-21</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">4:00:32</td><td class="nullValue">-</td></tr><tr class="even  79"><td class="dateTime">2022-09-21

      - 2022-09-26</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">3:36:52</td><td class="nullValue">-</td></tr><tr class="odd  80"><td class="dateTime">2022-09-26

      - 2022-10-06</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">10:15:57</td><td class="nullValue">-</td></tr><tr class="even  81"><td class="dateTime">2022-10-06

      - 2022-10-12</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">7:09:20</td><td class="nullValue">-</td></tr><tr class="odd  82"><td class="dateTime">2022-10-12

      - 2022-10-17</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">3:38:24</td><td class="nullValue">-</td></tr><tr class="even  83"><td class="dateTime">2022-10-17

      - 2022-10-25</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">7:46:52</td><td class="nullValue">-</td></tr><tr class="odd  84"><td class="dateTime">2022-10-25

      - 2022-10-31</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">3:40:41</td><td class="nullValue">-</td></tr><tr class="even  85"><td class="dateTime">2022-10-31

      - 2022-11-08</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">1:32:33</td><td class="nullValue">-</td></tr><tr class="odd  86"><td class="dateTime">2022-11-08

      - 2022-11-14</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">8:58:18</td><td class="nullValue">-</td></tr><tr class="even  87"><td class="dateTime">2022-11-14

      - 2022-11-21</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">4:43:39</td><td class="nullValue">-</td></tr><tr class="odd  88"><td class="dateTime">2022-11-21

      - 2022-11-28</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">3:02:13</td><td class="nullValue">-</td></tr><tr class="even  89"><td class="dateTime">2022-11-28

      - 2022-12-05</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">3:18:29</td><td class="nullValue">-</td></tr><tr class="odd  90"><td class="dateTime">2022-12-05

      - 2022-12-12</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">31:14:07</td><td class="nullValue">-</td></tr><tr class="even  91"><td class="dateTime">2022-12-12

      - 2022-12-19</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">3:32:36</td><td class="nullValue">-</td></tr><tr class="odd  92"><td class="dateTime">2022-12-19

      - 2022-12-26</td><td class="hms">0:00:03</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">12:33:21</td><td class="nullValue">-</td></tr><tr class="even  93"><td class="dateTime">2022-12-26

      - 2023-01-02</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">43:42:39</td><td class="nullValue">-</td></tr><tr class="odd  94"><td class="dateTime">2023-01-02

      - 2023-01-09</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">109:26:32</td><td class="nullValue">-</td></tr><tr class="even  95"><td class="dateTime">2023-01-09

      - 2023-01-16</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">62:54:37</td><td class="nullValue">-</td></tr><tr class="odd  96"><td class="dateTime">2023-01-16

      - 2023-01-23</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">49:52:41</td><td class="nullValue">-</td></tr><tr class="even  97"><td class="dateTime">2023-01-23

      - 2023-01-30</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">57:43:34</td><td class="nullValue">-</td></tr><tr class="odd  98"><td class="dateTime">2023-01-30

      - 2023-02-06</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">66:58:11</td><td class="nullValue">-</td></tr><tr class="even  99"><td class="dateTime">2023-02-06

      - 2023-02-13</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">9:09:00</td><td class="nullValue">-</td></tr><tr class="odd  100"><td class="dateTime">2023-02-13

      - 2023-02-20</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">11:02:48</td><td class="nullValue">-</td></tr><tr class="even  101"><td class="dateTime">2023-02-20</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr class="odd  102"><td class="dateTime">2023-02-21</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">0:29:55</td><td class="nullValue">-</td></tr><tr class="even  103"><td class="dateTime">2023-02-22</td><td class="hms">0:01:24</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">2:42:52</td><td class="nullValue">-</td></tr><tr class="odd  104"><td class="dateTime">2023-02-23</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">11:45:00</td><td class="nullValue">-</td></tr><tr class="even  105"><td class="dateTime">2023-02-24</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">13:56:17</td><td class="nullValue">-</td></tr><tr class="odd  106"><td class="dateTime">2023-02-25</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">16:13:27</td><td class="nullValue">-</td></tr><tr class="even  107"><td class="dateTime">2023-02-26</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">15:10:33</td><td class="nullValue">-</td></tr><tr class="odd  108"><td class="dateTime">2023-02-27</td><td class="hms">0:02:10</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">13:30:10</td><td class="nullValue">-</td></tr></table><h2>

      Battery capacity history

    </h2><div class="explanation">

      Charge capacity history of the system's batteries

    </div><table><colgroup><col/><col class="col2"/><col style="width: 10em;"/></colgroup><thead><tr><td><span>PERIOD</span></td><td class="centered">

            FULL CHARGE CAPACITY

          </td><td class="centered">

            DESIGN CAPACITY

          </td></tr></thead><tr class="even  1"><td class="dateTime">2021-02-15

      - 2021-02-22</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  2"><td class="dateTime">2021-02-22

      - 2021-03-01</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  3"><td class="dateTime">2021-03-01

      - 2021-03-08</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  4"><td class="dateTime">2021-03-08

      - 2021-03-15</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  5"><td class="dateTime">2021-03-15

      - 2021-03-22</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  6"><td class="dateTime">2021-03-22

      - 2021-03-29</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  7"><td class="dateTime">2021-03-29

      - 2021-04-05</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  8"><td class="dateTime">2021-04-05

      - 2021-04-12</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  9"><td class="dateTime">2021-04-12

      - 2021-04-19</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  10"><td class="dateTime">2021-04-19

      - 2021-04-26</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  11"><td class="dateTime">2021-04-26

      - 2021-05-03</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  12"><td class="dateTime">2021-05-03

      - 2021-05-10</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  13"><td class="dateTime">2021-05-10

      - 2021-05-17</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  14"><td class="dateTime">2021-05-17

      - 2021-05-24</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  15"><td class="dateTime">2021-05-24

      - 2021-05-31</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  16"><td class="dateTime">2021-05-31

      - 2021-06-07</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  17"><td class="dateTime">2021-06-07

      - 2021-06-14</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  18"><td class="dateTime">2021-06-14

      - 2021-06-21</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  19"><td class="dateTime">2021-06-21

      - 2021-06-28</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  20"><td class="dateTime">2021-06-28

      - 2021-07-05</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  21"><td class="dateTime">2021-07-05

      - 2021-07-12</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  22"><td class="dateTime">2021-07-12

      - 2021-07-19</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  23"><td class="dateTime">2021-07-19

      - 2021-07-26</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  24"><td class="dateTime">2021-07-26

      - 2021-08-02</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  25"><td class="dateTime">2021-08-02

      - 2021-08-09</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  26"><td class="dateTime">2021-08-09

      - 2021-08-16</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  27"><td class="dateTime">2021-08-16

      - 2021-08-23</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  28"><td class="dateTime">2021-08-23

      - 2021-08-30</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  29"><td class="dateTime">2021-08-30

      - 2021-09-06</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  30"><td class="dateTime">2021-09-06

      - 2021-09-13</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  31"><td class="dateTime">2021-09-13

      - 2021-09-20</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  32"><td class="dateTime">2021-09-20

      - 2021-09-27</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  33"><td class="dateTime">2021-09-27

      - 2021-10-04</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  34"><td class="dateTime">2021-10-04

      - 2021-10-11</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  35"><td class="dateTime">2021-10-11

      - 2021-10-18</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  36"><td class="dateTime">2021-10-18

      - 2021-10-25</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  37"><td class="dateTime">2021-10-25

      - 2021-11-01</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  38"><td class="dateTime">2021-11-01

      - 2021-11-08</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  39"><td class="dateTime">2021-11-08

      - 2021-11-15</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  40"><td class="dateTime">2021-11-15

      - 2021-11-22</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  41"><td class="dateTime">2021-11-22

      - 2021-11-29</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  42"><td class="dateTime">2021-11-29

      - 2021-12-06</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  43"><td class="dateTime">2021-12-06

      - 2021-12-13</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  44"><td class="dateTime">2021-12-13

      - 2021-12-20</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  45"><td class="dateTime">2021-12-20

      - 2021-12-27</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  46"><td class="dateTime">2021-12-27

      - 2022-01-03</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  47"><td class="dateTime">2022-01-03

      - 2022-01-10</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  48"><td class="dateTime">2022-01-10

      - 2022-01-24</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  49"><td class="dateTime">2022-01-24

      - 2022-02-02</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  50"><td class="dateTime">2022-02-02

      - 2022-02-07</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  51"><td class="dateTime">2022-02-07

      - 2022-02-14</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  52"><td class="dateTime">2022-02-14

      - 2022-02-21</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  53"><td class="dateTime">2022-02-21

      - 2022-02-28</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  54"><td class="dateTime">2022-02-28

      - 2022-03-07</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  55"><td class="dateTime">2022-03-07

      - 2022-03-15</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  56"><td class="dateTime">2022-03-15

      - 2022-03-28</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  57"><td class="dateTime">2022-03-28

      - 2022-04-04</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  58"><td class="dateTime">2022-04-04

      - 2022-04-11</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  59"><td class="dateTime">2022-04-11

      - 2022-04-18</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  60"><td class="dateTime">2022-04-18

      - 2022-04-25</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  61"><td class="dateTime">2022-04-25

      - 2022-05-02</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  62"><td class="dateTime">2022-05-02

      - 2022-05-09</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  63"><td class="dateTime">2022-05-09

      - 2022-05-16</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  64"><td class="dateTime">2022-05-16

      - 2022-05-23</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  65"><td class="dateTime">2022-05-23

      - 2022-05-30</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  66"><td class="dateTime">2022-05-30

      - 2022-06-06</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  67"><td class="dateTime">2022-06-06

      - 2022-06-16</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  68"><td class="dateTime">2022-06-16

      - 2022-06-21</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  69"><td class="dateTime">2022-06-21

      - 2022-07-04</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  70"><td class="dateTime">2022-07-04

      - 2022-07-15</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  71"><td class="dateTime">2022-07-15

      - 2022-07-18</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  72"><td class="dateTime">2022-07-18

      - 2022-07-25</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  73"><td class="dateTime">2022-07-25

      - 2022-08-01</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  74"><td class="dateTime">2022-08-01

      - 2022-08-08</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  75"><td class="dateTime">2022-08-08

      - 2022-08-22</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  76"><td class="dateTime">2022-08-22

      - 2022-09-01</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  77"><td class="dateTime">2022-09-01

      - 2022-09-08</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  78"><td class="dateTime">2022-09-08

      - 2022-09-21</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  79"><td class="dateTime">2022-09-21

      - 2022-09-26</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  80"><td class="dateTime">2022-09-26

      - 2022-10-06</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  81"><td class="dateTime">2022-10-06

      - 2022-10-12</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  82"><td class="dateTime">2022-10-12

      - 2022-10-17</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  83"><td class="dateTime">2022-10-17

      - 2022-10-25</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  84"><td class="dateTime">2022-10-25

      - 2022-10-31</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  85"><td class="dateTime">2022-10-31

      - 2022-11-08</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  86"><td class="dateTime">2022-11-08

      - 2022-11-14</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  87"><td class="dateTime">2022-11-14

      - 2022-11-21</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  88"><td class="dateTime">2022-11-21

      - 2022-11-28</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  89"><td class="dateTime">2022-11-28

      - 2022-12-05</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  90"><td class="dateTime">2022-12-05

      - 2022-12-12</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  91"><td class="dateTime">2022-12-12

      - 2022-12-19</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  92"><td class="dateTime">2022-12-19

      - 2022-12-26</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  93"><td class="dateTime">2022-12-26

      - 2023-01-02</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  94"><td class="dateTime">2023-01-02

      - 2023-01-09</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  95"><td class="dateTime">2023-01-09

      - 2023-01-16</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  96"><td class="dateTime">2023-01-16

      - 2023-01-23</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  97"><td class="dateTime">2023-01-23

      - 2023-01-30</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  98"><td class="dateTime">2023-01-30

      - 2023-02-06</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  99"><td class="dateTime">2023-02-06

      - 2023-02-13</td><td class="mw">3,626 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  100"><td class="dateTime">2023-02-13

      - 2023-02-20</td><td class="mw">3,469 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  101"><td class="dateTime">2023-02-20</td><td class="mw">3,370 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  102"><td class="dateTime">2023-02-21</td><td class="mw">3,370 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  103"><td class="dateTime">2023-02-22</td><td class="mw">3,370 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  104"><td class="dateTime">2023-02-23</td><td class="mw">3,370 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  105"><td class="dateTime">2023-02-24</td><td class="mw">3,370 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  106"><td class="dateTime">2023-02-25</td><td class="mw">3,370 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="even  107"><td class="dateTime">2023-02-26</td><td class="mw">3,370 mWh

        </td><td class="mw">4,400 mWh

        </td></tr><tr class="odd  108"><td class="dateTime">2023-02-27</td><td class="mw">3,370 mWh

        </td><td class="mw">4,400 mWh

        </td></tr></table><h2>

      Battery life estimates

    </h2><div class="explanation2">

      Battery life estimates based on observed drains

    </div><table><colgroup><col/><col class="col2"/><col style="width: 10em;"/><col style=""/><col style="width: 10em;"/><col style="width: 10em;"/><col style="width: 10em;"/></colgroup><thead><tr class="rowHeader"><td> </td><td colspan="2" class="centered">

            AT FULL CHARGE

          </td><td class="colBreak"> </td><td colspan="2" class="centered">

            AT DESIGN CAPACITY

          </td></tr><tr class="rowHeader"><td>

            PERIOD

          </td><td class="centered"><span>ACTIVE</span></td><td class="centered"><span>CONNECTED STANDBY</span></td><td class="colBreak"> </td><td class="centered"><span>ACTIVE</span></td><td class="centered"><span>CONNECTED STANDBY</span></td></tr></thead><tr style="vertical-align:top" class="even  1"><td class="dateTime">2021-02-15

      - 2021-02-22</td><td class="hms">1:54:51</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">2:19:22</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  2"><td class="dateTime">2021-02-22

      - 2021-03-01</td><td class="hms">2:54:01</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">3:31:10</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  3"><td class="dateTime">2021-03-01

      - 2021-03-08</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  4"><td class="dateTime">2021-03-08

      - 2021-03-15</td><td class="hms">2:29:45</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">3:01:44</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  5"><td class="dateTime">2021-03-15

      - 2021-03-22</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  6"><td class="dateTime">2021-03-22

      - 2021-03-29</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  7"><td class="dateTime">2021-03-29

      - 2021-04-05</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  8"><td class="dateTime">2021-04-05

      - 2021-04-12</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  9"><td class="dateTime">2021-04-12

      - 2021-04-19</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  10"><td class="dateTime">2021-04-19

      - 2021-04-26</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  11"><td class="dateTime">2021-04-26

      - 2021-05-03</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  12"><td class="dateTime">2021-05-03

      - 2021-05-10</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  13"><td class="dateTime">2021-05-10

      - 2021-05-17</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  14"><td class="dateTime">2021-05-17

      - 2021-05-24</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  15"><td class="dateTime">2021-05-24

      - 2021-05-31</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  16"><td class="dateTime">2021-05-31

      - 2021-06-07</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  17"><td class="dateTime">2021-06-07

      - 2021-06-14</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  18"><td class="dateTime">2021-06-14

      - 2021-06-21</td><td class="hms">2:11:44</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">2:39:52</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  19"><td class="dateTime">2021-06-21

      - 2021-06-28</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  20"><td class="dateTime">2021-06-28

      - 2021-07-05</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  21"><td class="dateTime">2021-07-05

      - 2021-07-12</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  22"><td class="dateTime">2021-07-12

      - 2021-07-19</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  23"><td class="dateTime">2021-07-19

      - 2021-07-26</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  24"><td class="dateTime">2021-07-26

      - 2021-08-02</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  25"><td class="dateTime">2021-08-02

      - 2021-08-09</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  26"><td class="dateTime">2021-08-09

      - 2021-08-16</td><td class="hms">4:31:57</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">5:30:00</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  27"><td class="dateTime">2021-08-16

      - 2021-08-23</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  28"><td class="dateTime">2021-08-23

      - 2021-08-30</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  29"><td class="dateTime">2021-08-30

      - 2021-09-06</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  30"><td class="dateTime">2021-09-06

      - 2021-09-13</td><td class="hms">4:31:57</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">5:30:00</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  31"><td class="dateTime">2021-09-13

      - 2021-09-20</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  32"><td class="dateTime">2021-09-20

      - 2021-09-27</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  33"><td class="dateTime">2021-09-27

      - 2021-10-04</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  34"><td class="dateTime">2021-10-04

      - 2021-10-11</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  35"><td class="dateTime">2021-10-11

      - 2021-10-18</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  36"><td class="dateTime">2021-10-18

      - 2021-10-25</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  37"><td class="dateTime">2021-10-25

      - 2021-11-01</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  38"><td class="dateTime">2021-11-01

      - 2021-11-08</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  39"><td class="dateTime">2021-11-08

      - 2021-11-15</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  40"><td class="dateTime">2021-11-15

      - 2021-11-22</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  41"><td class="dateTime">2021-11-22

      - 2021-11-29</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  42"><td class="dateTime">2021-11-29

      - 2021-12-06</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  43"><td class="dateTime">2021-12-06

      - 2021-12-13</td><td class="hms">4:42:01</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">5:42:13</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  44"><td class="dateTime">2021-12-13

      - 2021-12-20</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  45"><td class="dateTime">2021-12-20

      - 2021-12-27</td><td class="hms">3:03:06</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">3:42:11</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  46"><td class="dateTime">2021-12-27

      - 2022-01-03</td><td class="hms">3:01:08</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">3:39:48</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  47"><td class="dateTime">2022-01-03

      - 2022-01-10</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  48"><td class="dateTime">2022-01-10

      - 2022-01-24</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  49"><td class="dateTime">2022-01-24

      - 2022-02-02</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  50"><td class="dateTime">2022-02-02

      - 2022-02-07</td><td class="hms">0:11:40</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">0:14:09</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  51"><td class="dateTime">2022-02-07

      - 2022-02-14</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  52"><td class="dateTime">2022-02-14

      - 2022-02-21</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  53"><td class="dateTime">2022-02-21

      - 2022-02-28</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  54"><td class="dateTime">2022-02-28

      - 2022-03-07</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  55"><td class="dateTime">2022-03-07

      - 2022-03-15</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  56"><td class="dateTime">2022-03-15

      - 2022-03-28</td><td class="hms">1:59:05</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">2:24:30</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  57"><td class="dateTime">2022-03-28

      - 2022-04-04</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  58"><td class="dateTime">2022-04-04

      - 2022-04-11</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  59"><td class="dateTime">2022-04-11

      - 2022-04-18</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  60"><td class="dateTime">2022-04-18

      - 2022-04-25</td><td class="hms">2:01:24</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">2:27:19</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  61"><td class="dateTime">2022-04-25

      - 2022-05-02</td><td class="hms">2:09:35</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">2:37:15</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  62"><td class="dateTime">2022-05-02

      - 2022-05-09</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  63"><td class="dateTime">2022-05-09

      - 2022-05-16</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  64"><td class="dateTime">2022-05-16

      - 2022-05-23</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  65"><td class="dateTime">2022-05-23

      - 2022-05-30</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  66"><td class="dateTime">2022-05-30

      - 2022-06-06</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  67"><td class="dateTime">2022-06-06

      - 2022-06-16</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  68"><td class="dateTime">2022-06-16

      - 2022-06-21</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  69"><td class="dateTime">2022-06-21

      - 2022-07-04</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  70"><td class="dateTime">2022-07-04

      - 2022-07-15</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  71"><td class="dateTime">2022-07-15

      - 2022-07-18</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  72"><td class="dateTime">2022-07-18

      - 2022-07-25</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  73"><td class="dateTime">2022-07-25

      - 2022-08-01</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  74"><td class="dateTime">2022-08-01

      - 2022-08-08</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  75"><td class="dateTime">2022-08-08

      - 2022-08-22</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  76"><td class="dateTime">2022-08-22

      - 2022-09-01</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  77"><td class="dateTime">2022-09-01

      - 2022-09-08</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  78"><td class="dateTime">2022-09-08

      - 2022-09-21</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  79"><td class="dateTime">2022-09-21

      - 2022-09-26</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  80"><td class="dateTime">2022-09-26

      - 2022-10-06</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  81"><td class="dateTime">2022-10-06

      - 2022-10-12</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  82"><td class="dateTime">2022-10-12

      - 2022-10-17</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  83"><td class="dateTime">2022-10-17

      - 2022-10-25</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  84"><td class="dateTime">2022-10-25

      - 2022-10-31</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  85"><td class="dateTime">2022-10-31

      - 2022-11-08</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  86"><td class="dateTime">2022-11-08

      - 2022-11-14</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  87"><td class="dateTime">2022-11-14

      - 2022-11-21</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  88"><td class="dateTime">2022-11-21

      - 2022-11-28</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  89"><td class="dateTime">2022-11-28

      - 2022-12-05</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  90"><td class="dateTime">2022-12-05

      - 2022-12-12</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  91"><td class="dateTime">2022-12-12

      - 2022-12-19</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  92"><td class="dateTime">2022-12-19

      - 2022-12-26</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  93"><td class="dateTime">2022-12-26

      - 2023-01-02</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  94"><td class="dateTime">2023-01-02

      - 2023-01-09</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  95"><td class="dateTime">2023-01-09

      - 2023-01-16</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  96"><td class="dateTime">2023-01-16

      - 2023-01-23</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  97"><td class="dateTime">2023-01-23

      - 2023-01-30</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  98"><td class="dateTime">2023-01-30

      - 2023-02-06</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  99"><td class="dateTime">2023-02-06

      - 2023-02-13</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  100"><td class="dateTime">2023-02-13

      - 2023-02-20</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  101"><td class="dateTime">2023-02-20</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  102"><td class="dateTime">2023-02-21</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  103"><td class="dateTime">2023-02-22</td><td class="hms">2:42:41</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">3:32:24</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  104"><td class="dateTime">2023-02-23</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  105"><td class="dateTime">2023-02-24</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  106"><td class="dateTime">2023-02-25</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="even  107"><td class="dateTime">2023-02-26</td><td class="nullValue">-</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="nullValue">-</td><td class="nullValue">-</td></tr><tr style="vertical-align:top" class="odd  108"><td class="dateTime">2023-02-27</td><td class="hms">1:33:36</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">2:02:13</td><td class="nullValue">-</td></tr></table><div class="explanation2" style="margin-top: 1em; margin-bottom: 0.4em;">

      Current estimate of battery life based on all observed drains since OS install

    </div><table><colgroup><col/><col class="col2"/><col style="width: 10em;"/><col style=""/><col style="width: 10em;"/><col style="width: 10em;"/><col style="width: 10em;"/></colgroup><tr class="even" style="vertical-align:top"><td>

          Since OS install

        </td><td class="hms">1:21:57</td><td class="nullValue">-</td><td class="colBreak"> </td><td class="hms">1:47:00</td><td class="nullValue">-</td></tr></table><br/><br/><br/></body></html>
```
