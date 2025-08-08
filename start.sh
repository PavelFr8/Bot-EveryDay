echo "Проверяем доступность бота по HTTP..."

if wget --spider --timeout=5 --tries=3 http://bot.railway.internal:8000/; then
  echo "Бот доступен"
else
  echo "Бот недоступен"
fi

echo "Проверка с curl:"
curl -6 -I --max-time 5 http://bot.railway.internal:8000/

echo "Проверка порта 8000 с помощью nc:"
nc -z -v -w5 bot.railway.internal 8000 && echo "Порт открыт" || echo "Порт закрыт или нет доступа"
