26.08.24 
GNOME

**1.** **Базовая настройка**
Аккаунты Google и Mozilla, внешний вид/звуки/power, дата и время, языки, шорткаты 
- Тачпад 
	Settings (tap to click)
- Шорткат для терминала 
	gnome-terminal 
- Шорткат для языка 
	Tweaks -> Typing -> Switching to another layout (Alt+Shift)
- Иконки
	Расширение Desktop Icons NG
	// desktop файлы приложений лежат в /usr/share/applications
- Панель
	Dash to Panel

**2. Изменение разрешений и установка приложений**
- Добавление пользователя в sudoers 
	su nano /etc/sudoers (not safe but whatever) -> под # User privilege sertificate добавить alyson  ALL=(ALL:ALL) ALL
- Делаем так, чтобы sudo не запрашивал пароль
	в /etc/sudoers в конец файла добавить 
	alyson ALL=(ALL) NOPASSWD: ALL
- Установка менеджера пакетов snap //сперва хотелось поставить obsidian через него, но потом решила через AppImage; Canonical issues
	sudo apt-get install snap
- Установка Obsidian
	[[Установка приложений через AppImage]]
- Установка Telegram
	sudo apt search telegram //находим, что пакет называется telegram-desktop
	sudo apt-get install telegram-desktop
- Установка Chromium
	Просто через Software (GUI)
- Установка Brave 
	На оф. сайте рекомендуют делать через Curl
	- Установка Curl
		sudo apt install curl
	```
	sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
	echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main"|sudo tee /etc/apt/sources.list.d/brave-browser-release.list
	sudo apt update
	
	sudo apt install brave-browser
	```
- Установка AdGuardVPN через curl 
	curl -fsSL https://raw.githubusercontent.com/AdguardTeam/AdGuardVPNCLI/master/scripts/release/install.sh | sh -s -- -v
- Установка ProtonVPN
	wget https://repo.protonvpn.com/debian/dists/stable/main/binary-all/protonvpn-stable-release_1.0.4_all.deb
	sudo dpkg -i ./protonvpn-stable-release_1.0.4_all.deb && sudo apt update
	sudo apt-get install protonvpn-cli
- Установка Intellij IDEA через .tar.gz
	Просто распаковать и запустить
- Установка Dolphin из Software
- Разрешение для /usr/share/applications
	sudo chmod o+x applications
- Установка AndroidStudio через .tar.gz