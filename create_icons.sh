#!/bin/bash

# Создание папки для иконок
mkdir -p frontend/public/icons

# Создание placeholder иконок
sizes=(72 96 128 144 152 192 384 512)

for size in "${sizes[@]}"; do
    echo "# Placeholder icon ${size}x${size}" > "frontend/public/icons/icon-${size}x${size}.png"
    echo "✅ Создана иконка: icon-${size}x${size}.png"
done

echo "✅ Все иконки созданы!"
echo "⚠️  Это placeholder файлы. Замените на реальные PNG иконки для продакшена." 