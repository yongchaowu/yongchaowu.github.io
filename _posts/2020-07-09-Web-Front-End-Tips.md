---
layout: post
title: "Web-Front-End Tips"
date: 2020-07-09 20:54:00
categories: ["Web"]
tags: ["Front-End", "Web"]
---

## 调试前 确认浏览器大小
ctrl+0, 还原浏览器到100%，防止浏览器当前缩放过大或过小

<!--more-->
## &nbsp 空格占位
在html代码中&nbsp和空格的区别：
在html代码中每输入一个转义字符&nbsp就表示一个空格，输入十个&nbsp，页面中就显示10个空格位置。
而在html代码中输入空格，不管输入多少个空格，最终在页面中显示的空格位置只有一个
- 经测试： 三个&nbsp占位能补一个汉字

## style- float: left/right;
当在一行内横向排列两个或多个div时可以设置style“float:left/right”,其中本行最后一个div设置为right

## Reset Form
javascript:$('#resetAdminUserPasswdForm').form('clear')

##Redirect
- get
 - res.redirect([status,] path)
	其中参数：
	status：{Number}，表示要设置的HTTP状态码
	path：{String}，要设置到Location头中的URL
 - res.location(path)
- post
 未实现跳转代码。
 替代方案：
```
	 res.send({redirect: '/homePage'})

     var tmpData = JSON.parse(data);
     if(tmpData.error == undefined){
     if(typeof tmpData.redirect == 'string')
       window.location = tmpData.redirect;
     }
```

##html背景色渐变
[html背景色渐变](https://cloud.tencent.com/developer/article/1524323)
```
_background: #878d94;
background: -webkit-gradient(linear, 0 0, 0 100%, from(#878d94),to(#525352));
background: -moz-linear-gradient(top, #878d94, #525352);
background: -o-linear-gradient(top, #878d94, #525352);
background: -ms-linear-gradient(top, #878d94 0%, #525352 100%);
background: linear-gradient(top, #878d94, #525352);
filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#878d94',endColorstr='#525352');
```
## 网页动态背景：随鼠标线条变动
[src](https://blog.csdn.net/IT_model/article/details/89094941)
```html
<script type="text/javascript" src="https://cdn.bootcss.com/canvas-nest.js/1.0.1/canvas-nest.min.js"></script>

```
```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>动态线条背景</title>
</head>
<body>
    <h1>标题</h1>
</body>
<!--只加入下面这行-->
<script type="text/javascript" src="https://cdn.bootcss.com/canvas-nest.js/1.0.1/canvas-nest.min.js"></script>
</html>
```

## div右侧排列
让div元素靠右一般常用的有三种方法

- 第一种方法就是添加浮动float样式  `style:"float:right;"`
若是与下侧的div重合，可以考虑增加高度属性`style:"height:40px;"`
- 第二种方法就是添加外边距margin-right样式 `style:"margin-left:80%;"`
- 第三种方法就是设置position样式之absolute属性 `style:"position:absolute;"`

## 对话框居中显示
```
    $('#_Dlg').dialog('open');
    $('#_Dlg').window('vcenter');
    $('#_Dlg').dialog('move',{top:$(document).scrollTop() + 100});
```

## easyui中对于dialog页面传值的接收
[website](https://www.cnblogs.com/phoebej89/p/5235617.html)

```
A Page:
//详情查看
        function goToDetail(val) {
            //var url = '../Stock/CheckInventory/RandomCheckInventoryDetail.html?checksysno=' + val;
            var url = 'RandomCheckInventoryDetail.html';
            var title = '随机盘查明细【' + val + '】';

            //setPopFrameUrl(url, 1000, 550, title);
            $('#dd').dialog({
                title: title,
                width: 1000,
                height: 550,
                closed: false,
                cache: true,
                collapsible:true,
                href: url,
                queryParams: { checksysno: val },
                modal: true
            });
        }

B Page:
//获取页面url参数
        function getQueryParam(name) {
            var obj = $('#dd').dialog('options');
            var queryParams = obj["queryParams"];

            return queryParams[name];
        }
```

## easyUI 横向竖向分割线
```html
<div class="datagrid-toolbar"></div> 横向分割线
<div class="datagrid-btn-separator"/> 竖向分割线
```

## easyui-textbox /validatebox 赋值&取值
` $('#id').textbox().textbox('setValue', currPath);`
text-box设置值只能使用id选择器选择表单元素，然后使用textbox("setValue", value); 的方式设置值

很奇怪，如果先设置属性再赋值就可以：
```
    $('#id').textbox({width:350});
    $('#id').textbox('setValue', currPath);
```
表单元素使用easyui时，textbox和validatebox设置值和获取值的方式不一样
- 为text-box设置值只能使用id选择器选择表单元素，只能使用textbox("setValue", value) 或 textbox("setText", value) 的方式设置值，使用textbox("getValue") 或textbox("getText") 获取值；
- 为validatebox设置值可以使用id选择器和表单选择器，只能使用val()获取值和设置值。

## 获取Title
`$('#dlg').panel('options').title`


## html调整Label标签宽度
[website](https://blog.csdn.net/duanmuxiao/article/details/40045821)
`display为inline-block或者block,然后才可以设置长、宽`

## validatebox  验证类型扩展
```javascript
$.extend($.fn.validatebox.defaults.rules, {
 	ValueBetween: {
        validator: function(value, param){
            return value >= param[0] && value <= param[1] && /^\d+$/.test(value);
        },
        message: "\u5fc5\u987b\u5728{0}-{1}\u533a\u95f4"
    }
});

用法：data-options="validType:'ValueBetween[0,50]'"
```

## easyui datagrid 清空

删除数据
```javascript
var rows = $(id).datagrid('getRows');
for(var i=rows.length-1;i>=0;i--){
    var index = $('#dg_careersystem').datagrid('getRowIndex', rows[i]);  
    console.log("i="+i+"&index="+index);
    $(id).datagrid('deleteRow',index);
}
```
填充空数据：
`$('#dg_careersystem').datagrid('loadData',{total:0,rows:[]})`

## easyui PropertyGrid 表格内文字显示不全的内容
`data-options="nowrap:false"`

## EasyUI - datagrid中单元格里编辑控件的单击事件如何获取当前行的index
在一些特殊情况下，datagrid中默认获取当前行的方法onClickRow()并不能满足业务需求。
可先通过jquery获取父节点的方法parents()，获取该行tr标签，再通过attr()获取属性"datagrid-row-index"，即可获取index。
`var rowIndex = $(this).parents('.datagrid-row').attr('datagrid-row-index');`

## easyui +html input 文件导入
```
<label for="PathCnt" class="easyui-linkbutton" >程序文件</label>
<input id="PathCnt" type="file" accept="text" style="opacity: 0;width:60px">

Other:
$('#PathCnt').change(function(datas){

})
```
## 上传文件 用ajax传递formdata
```javascript
//// Web script
    //new FormData的参数是一个DOM对象，而非jQuery对象
    var formData = new FormData();
    //获取该input的所有元素、属性
	var f=document.getElementById("PathCnt");
    var FilePath = $('#PathCnt')[0].files[0];
    for ( var i = 0; i < f.files.length; i++) {
        var strname="file"+i;
    //判断文件是否符合要求
    // if (!/\.(swf|flv|mp4|rmvb|avi|mpeg|ra|ram|mov|wmv)$/.test(f.files[i].name)) {
    //   layer.alert("该上传的文件不是视频文件类型！", { icon: 5 , anim: 6 });
    //   break;
    //  }
    //将参数以键值对的形式添加到formData构造函数
    formData.append('uploadDatas', FilePath);
    formData.append(strname, f.files[i]);
    }
    console.log(f.files);

    var typeOfOS = 0;
	if(-1 != window.navigator.userAgent.indexOf('Windows')){
		typeOfOS = 1;
	}else if(-1 != window.navigator.userAgent.indexOf('Linux')){
		typeOfOS = 2;
	}

	$.ajax({
		url:'/Add?SystemType='+typeOfOS,
		type:'post',
		data:formData,
		processData:false,//对data参数进行序列化处理
		contentType:false,//不设置content-type请求头
        success:function(obj){
            debugger
        }
    })

////Background applications
var formidable = require('formidable');
var fs = require('fs');
var iconv = require('iconv-lite');

app.post('/Add', function(req, res){
    const form = new formidable.IncomingForm();
    form.keepExtensions = true;//保存扩展名
    form.maxFieldsSize = 500 * 1024 * 1024;//上传文件的最大大小
    form.parse(req, (err, fields, files) =>{
      if (err) {
        throw err;
      }
      let strFileName = files.uploadDatas.path;
      let readFile = fs.readFileSync(strFileName);
      if (req.query.SystemType == 1) {
        let bufferTemp = readFile;
        readFile = iconv.decode(bufferTemp, 'gbk');//.toString();
        let strEnter = "\n";
        if (readFile.indexOf("\r\n") != -1) {
          strEnter = "\r\n";
        }

        let objRow = readFile.split(strEnter);
        console.log(objRow);

        console.log('__dirname : ' + __dirname)
        console.log('cwd       : ' + process.cwd())
        try {
            var rc = fs.writeFileSync("./Data/"+files.uploadDatas.name,readFile);
          } catch (error) {
            return strPath + "写入失败，失败原因：" + error.message;
          }
        res.send({
            errCode:0
        })
      }
    })
});
```


## fs.writeFile
参数1需要写到文件名，e.g. ：../Data/T.txt
```javascript
    console.log('__dirname : ' + __dirname)
    console.log('cwd       : ' + process.cwd())
    try{
        var rc = fs.writeFileSync("../Data/T.txt",readFile);
    }catch (error) {
        return strPath + "写入失败，失败原因：" + error.message;
    }
```

## Html隐藏占空间与隐藏不占空间
```html
隐藏不占用空间：
display:none;
以下为示例代码：
<span style="display:none;">&nbsp;获取中</span>

隐藏占用空间：
visibility:hidden;
以下为示例代码：
<span style="visibility:hidden;">&nbsp;获取中</span>
————————————————
版权声明：本文为CSDN博主「刘德利_Android」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/u011967006/java/article/details/77156009
```

## JS如何设置元素样式的方法
```html
<div id="box"></div>

var box = document.getElementById("box");
box.style.width = '100px';
```
