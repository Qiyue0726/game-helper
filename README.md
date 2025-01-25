# 前言
该项目适用于大部分游戏的简单自动化，一定程度上可以达到养老护肝的效果。  
目前仅支持安卓模拟器（个人使用MuMu），桌面版由于 Windows 的版本更新，导致有很多问题，故而放弃。
项目内的截图和配置都适用于阴阳师，可以根据需要进行截图和相应的配置已适用于其它游戏。  

## 特别感谢
LuffyLSX 的 [auto-arknights](https://github.com/LuffyLSX/auto-arknights) 提供的图片识别技术;    

jajajag 的 [YYS-Helper](https://github.com/jajajag/YYS-Helper) 的项目架构参考;


## **警告：** 不保证一定不会被系统检测到，造成的一切后果请自行承担。  

# 使用方式
我的显示器是 4k(3840\*2160)，屏幕缩放设置为 150%，模拟器设置的是 1080P。
如果你的分辨率不同，可能需要重新截图，然后将截图替换文件夹中的图片，一定要保存为 png 格式。 
可以使用项目中的 adb.py 脚本来测试图片匹配的准确度。

除此之外，还需要安装以下 python 库
```
pip install opencv-python tqdm keyboard pure-python-adb
```

## 配置文件说明
```
// 文件名一定要以 config_xxx.json 为命名
// 除说明必填外，其它参数可以设置为null或直接不写
// found 和 notFound 即为 if 和 else，必须至少存在其中一个
// found 目前的参数仅支持图片嵌套 和 填写数字 表示单击次数
// found 和 notFound 可以参考配置里面的协作和标记处理

{
    "path":"2k/yuhun/",         // 必填，截图的路径，在 images 文件夹里
    "timeCost": 5,              // 一个完整流程的最少耗时,防止多次点击endFlag后计数不准
    "endFlag":"img",            // 必填，一个流程的最后一个识别图
    "failFlag": "fail",         // 必填，一个流程失败的识别图
    "stopFlag": ["stopImg"],    // 非必填，结束当前任务，字符串数组类型
    "failNum": 3,               // 非必填，失败次数，每失败若干次就弹窗警告，默认 10
    "refreshNum": 3,            // 必填（refreshConfig 存在时），刷新次数，用于配置主流程卡住时，执行副流程次数
    "refreshConfig": {}         // 非必填，副流程配置，与下面主流程配置方式相同
    "progressConfig: {          // 主流程配置
        "imgName":{                     // 需要识别的图片，img 为截图的文件名
                "similarity":0.95,      // 图片相似度，默认 0.9
                "exclusive": true,      // 是否主窗口专属，false 不进行检测
                "found":2,              // 如果找到图片进行的操作，可进行嵌套；'pass' 表示不处理
                "notFound":null,        // 找不到图片进行的操作，可进行嵌套
                "offsetX":30,           // 点击的坐标和识别图左上角横坐标的偏移量，默认 0
                "offsetY":-30,          // 点击的坐标和识别图左上角纵坐标的偏移量，默认 0
                "delay":0.1,            // 每点击一次后睡眠时间，默认 0，双击以上建议配置
                "checkAgain": false,    // 是否重复检测
                "checkImg": "fighting"  // 不重复检测的图片
            }
    }
    
}
```
