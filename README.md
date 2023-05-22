# lab3
## Подписка лайк и звезда на репо гита ♥
## Основные настройки

Первичная установка всего в **Alpine**:
```
apk add python3 py3-pip gcc g++ make linux-headers base-build py3-pandas py3-numpy
```

Далее копируем файлы с **Git**:

```
git clone https://github.com/BadKiko/lab3
```
>[!info] Важно что где вы выполните комманду там и будут файлы

Далее переходим в каталог скачанного репозитория:

```
cd lab3
```

Далее устанавливаем нужные зависимости **Python**:

```
python -r requirments.txt
```

## Настройка PostgreSQL

Далее необходимо настроить PostgreSQL чтобы предоставить скрипту доступ к файлам внутри VM

Для этого создайте NAT интерфейс:

- Добавьте новую сеть в вашу виртуальную машину![[Pasted image 20230522204534.png]]

- И настройте */etc/network/interfaces* примерно так:
```
auto lo 
iface lo inet loopback

auto eth1
iface eth1 inet dhcp

auto eth0
iface eth0 inet static address 172.16.1.3/24
gateway 172.16.1.1
```
>[!bug] ## Тут у вас могут быть другие IP и адаптеры
>Правильно настроить адаптеры можно будет если ввести 
> ```
> ip a
> ```
> Комманда выведет ваши интерфейсы
> Далее вам нужно будет сверить MAC адреса интерфейсов
> И настроить опираясь на них */etc/network/interfaces*

При правильной настройке вы включите NAT у машины PostgreSQL

## Запуск скрипта

Далее вам нужно будет просто запустить PostgreSQL от пользователя postgres
```
pg_ctl start
```

И запустить скрипт:
```
python main.py
```

