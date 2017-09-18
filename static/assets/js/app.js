$(function() {
$.ajaxSetup({beforeSend:function(request) {
                        if (localStorage.getItem("tokenval")) {
                              request.setRequestHeader("authkey",localStorage.getItem("tokenval"));
                        }
                    }
});
    // 读取body data-type 判断是哪个页面然后执行相应页面方法，方法在下面。
    var dataType = $('body').attr('data-type');
    console.log(dataType);
    $("#"+dataType).addClass("active");
    for (key in pageData) {
        if (key == dataType) {
            pageData[key]();
        }
    }
    $('body').attr('class','theme-white')

    autoLeftNav();
    $(window).resize(function() {
        autoLeftNav();
        console.log($(window).width())
    });

    //    if(storageLoad('SelcetColor')){

    //     }else{
    //       storageSave(saveSelectColor);
    //     }
})
function delhost(id) {
         $.ajax({
                url:'/deletehost?id='+id,
                type:'GET',
                success:function(data){
                console.log(data);
                if ( data.error == 1)
                {
                layer.msg(data.msg,{icon: 2});
                }else{
                layer.msg(data.msg,{icon: 1});
                }
               }
             });

}
function alogout() {
         $.ajax({
                url:'/logout',
                type:'GET',
                success:function(data){
                console.log(data);
                localStorage.clear(); 
                window.location.replace(data.loginurl); 
               }
             });

}


// 页面数据
var pageData = {
    // ===============================================
    // 首页
    // ===============================================
    'index': function indexData() {
 tables= $('#example-r').DataTable({
            bInfo: false, //页脚信息
            dom: 'ti',
            "order": [[ 0, "desc" ]],
            ajax: {
            url: '/api/eventinfo',
            dataSrc: 'eventdata'
            },
            columns: [
        { data: 'createtime',width:'20%'},
        { data: 'ip' ,width:'20%'},
        { data: 'event' ,width:'60%'}
                   ],
        language: {
            "sZeroRecords": "没有找到符合条件的数据",
            "sEmptyTable": "数据为空" 
            }
        });
function recreatetable() {
console.log("yes");
tables.ajax.reload();
}
setInterval(recreatetable,5000);
function loaditem(){
        try{
         $.ajax({
                url:'/localinfo',
                type:'GET',
                success:function(data){
                console.log(data);
                if (data.error==0){
               $('#cpuload').html(String(data.loadpercent)+'%');
               $('#cpuloadline').width(String(data.loadpercent)+'%');
               $('#diskload').html(String(data.diskpercent)+'%');
               $('#diskloadline').width(String(data.diskpercent)+'%');
               $('#memload').html(String(data.mempercent)+'%');
               $('#memloadline').width(String(data.mempercent)+'%');
               }else{
              layer.msg(data.msg);
              window.location.replace('/login'); 
}
}
             });
}
catch (e) {
console.log(e.message);
}
}
loaditem();
setInterval(loaditem,5000);

        var echartsA = echarts.init(document.getElementById('tpl-echarts'));
        option = {
            tooltip: {
                trigger: 'axis'
            },
            grid: {
                top: '3%',
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: [{
                type: 'category',
                boundaryGap: false,
                data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            }],
            yAxis: [{
                type: 'value'
            }],
            textStyle: {
                color: '#838FA1'
            },
            series: [{
                name: '邮件营销',
                type: 'line',
                stack: '总量',
                areaStyle: { normal: {} },
                data: [120, 132, 101, 134, 90],
                itemStyle: {
                    normal: {
                        color: '#1cabdb',
                        borderColor: '#1cabdb',
                        borderWidth: '2',
                        borderType: 'solid',
                        opacity: '1'
                    },
                    emphasis: {

                    }
                }
            }]
        };

        echartsA.setOption(option);
    },
    'alarmset': function alarmset(){
$('#alarmbutton').click(
function(){
console.log(this);
var times=$("#alarmtimes").val();

$.ajax({
                url:'/api/changesettings',
                type:'POST',
                data:{
                    times:times
                },
                success:function(data){
                if ( data.error == 1)
                {
                layer.msg(data.msg,{icon: 2});
                }else{
                layer.msg(data.msg,{icon: 1});
                location.reload()
                }
                           }
                });

});
},
"threshold": function threshold() {
$('#memrange').jRange({
    from: 0.0,
    to: 100.0,
    step: 0.5,
    scale: [0.0,10.0,20.0,30.0,40.0,50.0,60.0,70.0,80.0,90.0,100.0],
    format: '%s',
    width: 400,
    showLabels: true,
    snap: true
});


},
    'widgets': function indexData() {
 hosttables= $('#example-r').DataTable({
            ajax: {
            url: '/api/hostlistinfo',
            async:false,
            dataSrc: 'hostinfodata'
            },
            columns: [
        { data: 'ip' ,width:'20%'},
        { data: 'description',width:'10%'},
        { data: 'status',width:'10%' ,"render": function (data, type, row, meta) {
           if (data==0){
           return data ='<i class="fa fa-circle" aria-hidden="true" style="color:green;"></i>'}
else
{
return data ='<i class="fa fa-circle" aria-hidden="true" style="color:red;"></i>'
}
}
},
        { data: 'enabled' ,width:'20%',"render":function (data, type, row, meta) {
           if (data.split("^")[1]=="True"){
           return data ='<input id="switch-state" data-size="xs" data-hostid='+data.split("^")[0]+' type="checkbox" checked />'}
else
{
return data ='<input id="switch-state"   data-size="xs" data-hostid='+data.split("^")[0]+' type="checkbox" />'
}
}
},
        { data: 'updatetime' ,width:'20%'},
        { data: 'id' ,width:'20%',"orderable": false,"render": function (data, type, row, meta) {
           return data ='<div class="tpl-table-black-operation"> <a href="/hostdetails?id='+data+'"><i class="am-icon-pencil"></i> 详情</a><a href="javascript:;" onclick="delhost('+data+')" class="tpl-table-black-operation-del"><i class="am-icon-trash"></i> 删除</a></div>'
        }
}
                   ],
        language: {
            "sZeroRecords": "没有找到符合条件的数据",
            "sEmptyTable": "数据为空" 
            }
        });
$('#switch-state').bootstrapSwitch();
function recreatetable() {
hosttables.ajax.reload();
$('#switch-state').bootstrapSwitch();
$('#switch-state').on('switchChange.bootstrapSwitch', function(event, state) {
  var hostid=$(this).data("hostid");
$.ajax({
                url:'/api/changeswitch',
                type:'POST',
                data:{
                    hostid:hostid,state:state
                },
                success:function(data){
                if ( data.error == 1)
                {
                layer.msg(data.msg,{icon: 2});
                }else{
                layer.msg(data.msg);
                }
                           }
                });
  
});
}
setInterval(recreatetable,30000);
$('#switch-state').on('switchChange.bootstrapSwitch', function(event, state) {
var hostid=$(this).data("hostid");
$.ajax({
                url:'/api/changeswitch',
                type:'POST',
                data:{
                    hostid:hostid,state:state
                },
                success:function(data){
                if ( data.error == 1)
                {
                layer.msg(data.msg,{icon: 2});
                }else{
                layer.msg(data.msg,{icon: 1});
                }
                           }
                });
});
},
     "hosttree": function hosttree(){

var hostid = $('body').attr('data-id');
function zTreeOnClick(event, treeId, treeNode) {
    $('body').attr('data-id',treeNode.id);
    hostid = $('body').attr('data-id');
    var stateObject = {};
    var title = "";
    var newUrl = "/hostdetails?id="+hostid;
    history.pushState(stateObject,title,newUrl);
    recircliful(); 
    var treeObj = $.fn.zTree.getZTreeObj(treeId);
    var nodes = treeObj.getSelectedNodes();
    console.log(nodes);
    for (var i=0, l=nodes.length; i < l; i++) {
    	treeObj.checkNode(nodes[i], true, true);
    }
};
var setting = {
check: {
                enable: true,
                chkStyle: "radio",
                radioType: "all"
        },
        view: {
                showLine: false
        },
        callback: {
		onClick: zTreeOnClick
	},
        data: {
                simpleData: {
                        enable: true
                }
        }
};

function gettreedata() {
         $.ajax({
                url:'/treedata?id='+hostid,
                type:'GET',
                async: false,
                success:function(data){
                zNodes= data;
               }
             });
         return zNodes;
};

$.fn.zTree.init($("#treeDemo"), setting,gettreedata()); 
         $.ajax({
                url:'/api/realtimeinfo?id='+hostid,
                type:'GET',
                success:function(data){
                console.log(data);
               }
             });
diskvar={"animation": 0,
            "animationStep": 5,
            "foregroundBorderWidth": 6,
            "backgroundColor": "none",
            "fillColor": "#eee",
            "percent": 38,
            "textSize": 28,
            "textColor": "#666",
            "icon": "f0a0",
            "iconPosition": "middle",
            "textStyle":"font-size:19px;",
            "text": "Space Left",
           "textBelow": true}
memvar={"animation": 0,
            "animationStep": 5,
            "foregroundBorderWidth": 6,
            "backgroundColor": "none",
            "fillColor": "#eee",
            "percent": 38,
            "textSize": 28,
            "textColor": "#666",
            "icon": "f23a",
            "iconPosition": "middle",
            "textStyle":"font-size:19px;",
            "text": "Mem Left",
           "textBelow": true}
cachevar={"animation": 0,
            "animationStep": 5,
            "foregroundBorderWidth": 6,
            "backgroundColor": "none",
            "fillColor": "#eee",
            "percent": 38,
            "textSize": 28,
            "textColor": "#666",
            "icon": "f2d5",
            "iconPosition": "middle",
            "textStyle":"font-size:19px;",
            "text": "Cache Left",
           "textBelow": true}
loadvar={"animation": 0,
            "animationStep": 5,
            "foregroundBorderWidth": 6,
            "backgroundColor": "none",
            "fillColor": "#eee",
            "percent": 38,
            "textSize": 28,
            "textColor": "#666",
            "icon": "f0ae",
            "iconPosition": "middle",
            "textStyle":"font-size:19px;",
            "text": "Load Left",
           "textBelow": true}
         $.ajax({
                url:'/api/realtimeinfo?id='+hostid,
                type:'GET',
                success:function(data){
diskvar.percent=data.diskusage;
memvar.percent=data.memusage;
cachevar.percent=data.cacheusage;
loadvar.percent=data.loadusage;
$("#test-circle").circliful(diskvar);
$("#test-circle1").circliful(memvar);
$("#test-circle2").circliful(cachevar);
$("#test-circle3").circliful(loadvar);
               }
             });

function recircliful() {
         $.ajax({
                url:'/api/realtimeinfo?id='+hostid,
                type:'GET',
                success:function(data){
console.log(data)
diskvar.percent=data.diskusage;
memvar.percent=data.memusage;
cachevar.percent=data.cacheusage;
loadvar.percent=data.loadusage;
$("#test-circle").empty();
$("#test-circle").circliful(diskvar);
$("#test-circle1").empty();
$("#test-circle1").circliful(memvar);
$("#test-circle2").empty();
$("#test-circle2").circliful(cachevar);
$("#test-circle3").empty();
$("#test-circle3").circliful(loadvar);
               }
             });
}
setInterval(recircliful,2000);
var echartsA = echarts.init(document.getElementById('tpl-echarts'));
var echartsB = echarts.init(document.getElementById('tpl-echarts1'));
var echartsC = echarts.init(document.getElementById('tpl-echarts2'));
options = {
    tooltip : {
        trigger: 'axis',
        axisPointer: {
            type: 'cross',
            label: {
                backgroundColor: '#6a7985'
            }
        }
    },
    legend: {
        data:['邮件营销','联盟广告','视频广告','直接访问','搜索引擎']
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis : [
        {
            type : 'category',
            boundaryGap : false,
            data : ['周一','周二','周三','周四','周五','周六','周日']
        }
    ],
    yAxis : [
        {
            type : 'value'
        }
    ],
    series : [
        {
            name:'邮件营销',
            type:'line',
            stack: '总量',
            areaStyle: {normal: {}},
            data:[120, 132, 101, 134, 90, 230, 210]
        },
        {
            name:'联盟广告',
            type:'line',
            stack: '总量',
            areaStyle: {normal: {}},
            data:[220, 182, 191, 234, 290, 330, 310]
        },
        {
            name:'视频广告',
            type:'line',
            stack: '总量',
            areaStyle: {normal: {}},
            data:[150, 232, 201, 154, 190, 330, 410]
        },
        {
            name:'直接访问',
            type:'line',
            stack: '总量',
            areaStyle: {normal: {}},
            data:[320, 332, 301, 334, 390, 330, 320]
        },
        {
            name:'搜索引擎',
            type:'line',
            stack: '总量',
            label: {
                normal: {
                    show: true,
                    position: 'top'
                }
            },
            areaStyle: {normal: {}},
            data:[820, 932, 901, 934, 1290, 1330, 1320]
        }
    ]
};
echartsA.setOption(options);
echartsB.setOption(options);
echartsC.setOption(options);
window.addEventListener("resize", function () {
echartsA.resize();
echartsB.resize();
echartsC.resize();
 });
},
    "login": function login() {
       $('#submitbutton').on('click', function(){ 
         var username=$('#user-name').val();
         var password=$('#user-pass').val();
         logindata=$.ajax({
                url:'/login',
                type:'POST',
                async:false,
                data:{
                    username:username,password:password
                },
                success:function(data){
                if ( data.error == 1)
                {
                layer.msg(data.msg,{icon: 2});
                }else{
                localStorage.clear();
                localStorage.setItem("tokenval",data.token);
                layer.msg("登陆成功",{icon: 1,time: 3000});
                window.location.replace(data.nexturl);
                }
                           }
                });
      }); 
      $(document).keypress(function(e) {
       var eCode = e.keyCode ? e.keyCode : e.which ? e.which : e.charCode;
        if (eCode == 13){
         var username=$('#user-name').val();
         var password=$('#user-pass').val();
         $.ajax({
                url:'/login',
                type:'POST',
                data:{
                    username:username,password:password
                },
                success:function(data){
                if ( data.error == 1)
                {
                layer.msg(data.msg,{icon: 2});
                }else{
                localStorage.clear();
                localStorage.setItem("tokenval",data.token);
                layer.msg("登陆成功",{icon: 1,time: 3000});
                window.location.replace(data.nexturl);
                }
}
                });
        
                    }
                    });
},
    // ===============================================
    // 图表页
    // ===============================================
    'chart': function chartData() {
        // ==========================
        // 百度图表A http://echarts.baidu.com/
        // ==========================

        var echartsC = echarts.init(document.getElementById('tpl-echarts-C'));


        optionC = {
            tooltip: {
                trigger: 'axis'
            },

            legend: {
                data: ['蒸发量', '降水量', '平均温度']
            },
            xAxis: [{
                type: 'category',
                data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
            }],
            yAxis: [{
                    type: 'value',
                    name: '水量',
                    min: 0,
                    max: 250,
                    interval: 50,
                    axisLabel: {
                        formatter: '{value} ml'
                    }
                },
                {
                    type: 'value',
                    name: '温度',
                    min: 0,
                    max: 25,
                    interval: 5,
                    axisLabel: {
                        formatter: '{value} °C'
                    }
                }
            ],
            series: [{
                    name: '蒸发量',
                    type: 'bar',
                    data: [2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 135.6, 162.2, 32.6, 20.0, 6.4, 3.3]
                },
                {
                    name: '降水量',
                    type: 'bar',
                    data: [2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3]
                },
                {
                    name: '平均温度',
                    type: 'line',
                    yAxisIndex: 1,
                    data: [2.0, 2.2, 3.3, 4.5, 6.3, 10.2, 20.3, 23.4, 23.0, 16.5, 12.0, 6.2]
                }
            ]
        };

        echartsC.setOption(optionC);

        var echartsB = echarts.init(document.getElementById('tpl-echarts-B'));
        optionB = {
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                x: 'center',
                data: ['某软件', '某主食手机', '某水果手机', '降水量', '蒸发量']
            },
            radar: [{
                    indicator: [
                        { text: '品牌', max: 100 },
                        { text: '内容', max: 100 },
                        { text: '可用性', max: 100 },
                        { text: '功能', max: 100 }
                    ],
                    center: ['25%', '40%'],
                    radius: 80
                },
                {
                    indicator: [
                        { text: '外观', max: 100 },
                        { text: '拍照', max: 100 },
                        { text: '系统', max: 100 },
                        { text: '性能', max: 100 },
                        { text: '屏幕', max: 100 }
                    ],
                    radius: 80,
                    center: ['50%', '60%'],
                },
                {
                    indicator: (function() {
                        var res = [];
                        for (var i = 1; i <= 12; i++) {
                            res.push({ text: i + '月', max: 100 });
                        }
                        return res;
                    })(),
                    center: ['75%', '40%'],
                    radius: 80
                }
            ],
            series: [{
                    type: 'radar',
                    tooltip: {
                        trigger: 'item'
                    },
                    itemStyle: { normal: { areaStyle: { type: 'default' } } },
                    data: [{
                        value: [60, 73, 85, 40],
                        name: '某软件'
                    }]
                },
                {
                    type: 'radar',
                    radarIndex: 1,
                    data: [{
                            value: [85, 90, 90, 95, 95],
                            name: '某主食手机'
                        },
                        {
                            value: [95, 80, 95, 90, 93],
                            name: '某水果手机'
                        }
                    ]
                },
                {
                    type: 'radar',
                    radarIndex: 2,
                    itemStyle: { normal: { areaStyle: { type: 'default' } } },
                    data: [{
                            name: '降水量',
                            value: [2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 75.6, 82.2, 48.7, 18.8, 6.0, 2.3],
                        },
                        {
                            name: '蒸发量',
                            value: [2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 35.6, 62.2, 32.6, 20.0, 6.4, 3.3]
                        }
                    ]
                }
            ]
        };
        echartsB.setOption(optionB);
        var echartsA = echarts.init(document.getElementById('tpl-echarts-A'));
        option = {

            tooltip: {
                trigger: 'axis',
            },
            legend: {
                data: ['邮件', '媒体', '资源']
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: [{
                type: 'category',
                boundaryGap: true,
                data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
            }],

            yAxis: [{
                type: 'value'
            }],
            series: [{
                    name: '邮件',
                    type: 'line',
                    stack: '总量',
                    areaStyle: { normal: {} },
                    data: [120, 132, 101, 134, 90, 230, 210],
                    itemStyle: {
                        normal: {
                            color: '#59aea2'
                        },
                        emphasis: {

                        }
                    }
                },
                {
                    name: '媒体',
                    type: 'line',
                    stack: '总量',
                    areaStyle: { normal: {} },
                    data: [220, 182, 191, 234, 290, 330, 310],
                    itemStyle: {
                        normal: {
                            color: '#e7505a'
                        }
                    }
                },
                {
                    name: '资源',
                    type: 'line',
                    stack: '总量',
                    areaStyle: { normal: {} },
                    data: [150, 232, 201, 154, 190, 330, 410],
                    itemStyle: {
                        normal: {
                            color: '#32c5d2'
                        }
                    }
                }
            ]
        };
        echartsA.setOption(option);
    }
}


// 风格切换

$('.tpl-skiner-toggle').on('click', function() {
    $('.tpl-skiner').toggleClass('active');
})

$('.tpl-skiner-content-bar').find('span').on('click', function() {
    $('body').attr('class', $(this).attr('data-color'))
    saveSelectColor.Color = $(this).attr('data-color');
    // 保存选择项
    storageSave(saveSelectColor);

})




// 侧边菜单开关


function autoLeftNav() {



    $('.tpl-header-switch-button').on('click', function() {
        if ($('.left-sidebar').is('.active')) {
            if ($(window).width() > 1024) {
                $('.tpl-content-wrapper').removeClass('active');
            }
            $('.left-sidebar').removeClass('active');
        } else {

            $('.left-sidebar').addClass('active');
            if ($(window).width() > 1024) {
                $('.tpl-content-wrapper').addClass('active');
            }
        }
    })

    if ($(window).width() < 1024) {
        $('.left-sidebar').addClass('active');
    } else {
        $('.left-sidebar').removeClass('active');
    }
}


// 侧边菜单
$('.sidebar-nav-sub-title').on('click', function() {
    $(this).siblings('.sidebar-nav-sub').slideToggle(80)
        .end()
        .find('.sidebar-nav-sub-ico').toggleClass('sidebar-nav-sub-ico-rotate');
})
