На примере Obsidian
1) Скачивание образа Obsidian-1.6.7.AppImage
2) chmod u+x Obsidian-1.6.7.AppImage
3) Создание obsidian.desktop (предварительно скачиваем иконку в .svg): 
```
[Desktop Entry]
Name=Obsidian
Exec=/home/alyson/Applications/Obsidian/Obsidian-1.6.7.AppImage
Icon=/home/alyson/Applications/obsidian-icon.svg
Type=Application
Categories=GTK;GNOME;Utility;
```
4) Копирование obsidian.desktop на рабочий стол и в /usr/share/applications (последнее для доступа из панели приложений)