# 前言
该项目适用于大部分游戏的简单自动化，一定程度上可以达到养老护肝的效果。  
项目内的截图和配置都适用于阴阳师，可以根据需要进行截图和相应的配置已适用于其它游戏。  

## 特别感谢
LuffyLSX 的 [auto-arknights](https://github.com/LuffyLSX/auto-arknights) 提供的图片识别技术;    

jajajag 的 [YYS-Helper](https://github.com/jajajag/YYS-Helper) 的项目架构参考;


## **警告：** 不保证一定不会被系统检测到，造成的一切后果请自行承担。  

# 使用方式
由于我使用的显示器是 2k(2560\*1440) 的,所以如果你使用的是 1080P(1920\*1080) 或其它分辨率的显示器，请修改 `helper.py` 中的 `device_width` 和 `device_height`。   

如果分辨率不同，除了修改文件外，还需要将游戏全屏，然后截图替换文件夹中的图片，一定要保存为 bmp 格式。  

## 配置文件说明
```
// 文件名一定要以 config_xxx.json 为命名
{
    "path":"2k/yuhun/", // 截图的路径,在 images 文件夹里
    "endFlag":"end",    // 一个流程的最后一个识别图
    "img":{             // 需要识别的图片
        "found":"click",// 如果找到图片进行的操作，可进行嵌套
        "notFound":"",  // 找不到图片进行的操作，可进行嵌套
        "offsetX":"",   // 识别图的横坐标偏移量
        "offsetY":""
    }
}
```
