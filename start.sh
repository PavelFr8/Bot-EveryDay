#!/bin/sh

echo "Проверяем доступность бота..."

# Пытаемся достучаться до бота с таймаутом 5 секунд
if wget --spider --timeout=5 --tries=3 http://bot.railway.internal:8000/; then
  echo "Бот доступен, запускаем nginx..."
  exec nginx -g 'daemon off;'
else
  echo "Бот недоступен, перезапускаемся через 10 секунд..."
  sleep 10
  exec /start.sh
fi
