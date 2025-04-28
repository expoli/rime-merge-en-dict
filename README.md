# rime-en_dicts

rime 方案的 en_dicts 分布在各个的方案中，每次加词都是在单个方案词库中进行加词，所以在使用了一段时间之后，总会发现在一个方案中加的词在另一个方案中无法使用，于是就创建了这个合并词库。

## 项目背景

Rime 输入法的英文词库分散在各个不同的方案中，导致用户在不同方案之间切换时，无法共享自定义的英文词汇。为了解决这个问题，我们创建了这个项目，旨在合并各个方案的英文词库，实现词汇共享。

## 使用方法

在 release 中下载即可使用，放置到你需要的目录中，然后在你的 Rime 配置文件中导入该词库。

## 万象输入法配置示例

```yaml
name: wanxiang_en
version: "2023-05-09"
import_tables:
  - en_dicts/en_merge # 英文主词库
```

## 贡献指南

欢迎提交 PR 来完善本项目，请确保：
- 修改内容符合项目目标
- 代码风格一致
- 提供清晰的提交信息

## 相关项目

- [iDvel/rime-ice](https://github.com/iDvel/rime-ice)
- [rimeinn/rime-moran](https://github.com/rimeinn/rime-moran)
- [amzxyz/rime_wanxiang](https://github.com/amzxyz/rime_wanxiang)
