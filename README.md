# What is this?

メールでオープンソースのソーシャルブックマークScuttleへの登録を行います。

Facebookからの「今週の保存」のお知らせメールからもScuttleへの登録ができます。


# 使い方
$HOME/.procmail などに登録して使います。

## .procmailのレシピの例

```
#
#scuttle bookmark登録 転送処理
#
:0 c
* ^From: "Facebook" <notification.*@facebookmail.com>
* ^Reply-to: noreply <noreply@facebookmail.com>
| $HOME/bin/mailToScuttle.py https://example.com/scuttle/ user pass

:0
* ^To: .*scuttle@example.com
| $HOME/bin/mailToScuttle.py https://example.com/scuttle/ user pass
```
