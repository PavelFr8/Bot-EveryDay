#!/bin/sh

echo "=== Проверка прослушиваемых портов (ss -tlnp) ==="
ss -tlnp || netstat -tlnp

echo "=== Проверка запущенных процессов nginx ==="
ps aux | grep nginx

echo "=== Проверка конфигурации nginx ==="
nginx -t

echo "=== Проверка логов nginx (последние 20 строк) ==="
tail -20 /var/log/nginx/error.log || echo "Нет файла логов nginx"

echo "=== Проверяем доступность бота локально ==="
curl -v http://bot.railway.internal:8000/ || echo "curl не удался"

# Проверка доступности бота для старта nginx
if wget --spider --timeout=5 --tries=3 http://bot.railway.internal:8000/; then
  echo "Бот доступен, запускаем nginx..."
  exec nginx -g 'daemon off;'
else
  echo "Бот недоступен, перезапускаемся через 10 секунд..."
  sleep 10
  exec /start.sh
fi
