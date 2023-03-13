
# Модель сохраненных коротких ссылок
# NAME ShortLink
# id
# short_url
# original_url
# "type": "<public|private>"
# "user" Optional FK (User)
# active true/false

# Модель с логом достуав к коротким ссылкам
# NAME AccessLog
# id
# FK (ShortLink)
# "connection_info"
# "connection_dt"

# Модель Пользователя
# https://fastapi-users.github.io/fastapi-users/10.4/configuration/databases/sqlalchemy/
# NAME User
# email
# password
