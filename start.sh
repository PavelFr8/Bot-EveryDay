#!/bin/sh

echo "Проверяем доступность бота..."

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://bot.railway.internal:8000/)

if [ "$HTTP_STATUS" -ge 200 ] && [ "$HTTP_STATUS" -lt 600 ]; then
  echo "Бот доступен с HTTP статусом $HTTP_STATUS, запускаем nginx..."
  exec nginx -g 'daemon off;'
else
  echo "Бот недоступен (HTTP статус: $HTTP_STATUS), перезапускаемся через 10 секунд..."
  sleep 10
  exec /start.sh
fi
