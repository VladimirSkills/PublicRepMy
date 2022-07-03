from conftest import do_repeat_it, add_file_log  # импортируем декораторы
from app.settings import valid_email, valid_password
import inspect  # используем метод для возвращения имени функции
import requests
import pytest
import time
import json
import os  # используем для работы с каталогами (save photo path)

class PetFriends:
    """Библиотека веб приложения Pet Friends"""

    def __init__(self):
        """ФИЧА-1 / шаг 1. Создаём переменную idp, чтобы можно было добавить
        фото к id именно этого созданного питомца"""
        self.idp = ""  # ФИЧА-1
        self.base_url = "https://petfriends.skillfactory.ru/"


    # Добавление питомца без фото - ФИЧА-1
    def post_add_pet_nofoto(self, auth_key: json, name: str, animal_type: str, age: str) -> json:

        headers = {'auth_key': auth_key['key']}
        data = {'name': name, 'animal_type': animal_type, 'age': age}
        res = requests.post(self.base_url + 'api/create_pet_simple', data=data, headers=headers)
        status = res.status_code
        try:
            result = res.json()
            """ФИЧА-1 / шаг 2. Передаём значение id созданного питомца в переменную idp"""
            self.idp = res.json().get("id")
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result

    # Добавление фото к созданному питомцу без фото - ФИЧА-1
    def post_add_pet_photo(self, auth_key: json, pet_photo: str) -> json:
        headers = {'auth_key': auth_key['key']}
        """ФИЧА-1 / шаг 3. Передаём id созданного питомца(idp) в качестве параметра на добавление фото"""
        pet_id = self.idp
        files = {"pet_photo": open(pet_photo, "rb")}
        res = requests.post(self.base_url + 'api/pets/set_photo/' + pet_id, files=files, headers=headers)
        status = res.status_code
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result



    # Изменение фото первого питомца в списке - ФИЧА-2
    """Выносим pet_id в аргументы функции..."""
    def change_pet_photo(self, auth_key: json, pet_photo: str, pet_id: str) -> json:
        headers = {'auth_key': auth_key['key']}
        files = {"pet_photo": open(pet_photo, "rb")}
        res = requests.post(self.base_url + 'api/pets/set_photo/' + pet_id, files=files, headers=headers)
        status = res.status_code
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result


    # Добавление питомца с фото без применения MultipartEncoder - ФИЧА-3
    # А также пример запроса на получение данных по дополнительным заголовкам - ФИЧА-4
    def add_new_pet_with_photo(self, auth_key: json, name: str, animal_type: str, age: str, pet_photo: str) -> json:
        headers = {'auth_key': auth_key['key']}
        data = {'name': name, 'animal_type': animal_type, 'age': age}
        files = {"pet_photo": open(pet_photo, "rb")}
        res = requests.post(self.base_url + 'api/pets', data=data, files=files, headers=headers)
        content = res.headers
        optional = res.request.headers
        url = res.request.url
        status = res.status_code
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        return status, result, content, optional, url


"""<<<<<< Примеры ТЕСТов для запросов >>>>>>>"""

pf = PetFriends()
# Для запуска тестов нужно добавить запрос на получение ключа: pf.get_api_key (см. учебку)

"""Тестируем: Добавление фото к созданному питомцу без фото => post_add_pet_photo
Для этого теста и требовалось определение id/idp для конкретно созданного питомца - в первых двух запросах...ФИЧА-1"""
def test_post_add_petfoto(pet_photo=r'../images/king-kong1.jpg'):
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Добавляем фото
    status, result = pf.post_add_pet_photo(auth_key, pet_photo)
    # Получаем значение картинки1:
    value_image1 = result.get('pet_photo')
    print('\n', f"value_image1: {len(value_image1)} символов: {value_image1}", sep='')
    # Добавляем новое фото:
    _, result2 = pf.post_add_pet_photo(auth_key, r'../images/king-kong3.jpg')
    # Получаем значение картинки2:
    value_image2 = result2.get('pet_photo')
    print(f"value_image2: {len(value_image2)} символов: {value_image2}")
    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    # Если полученное значение ключа одной картинки не равно значению ключа другой картинки - PASSED:
    assert value_image1 != value_image2


"""Тестируем: Изменение фото первого питомца в списке => change_pet_photo => ФИЧА-2"""
# Для запуска нужно в т.ч. добавить запрос на получение списка питомцев: get_list_of_pets
def test_changes_petfoto(pet_photo=r'../images/king-kong3.jpg'):
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = my_pets['pets'][0]['id']  # id изменяемого питомца (первый в списке)
    value_image1 = my_pets['pets'][0]['pet_photo']  # получаем код image изменяемой фотки
    print(f"\nvalue_image1: {len(str(value_image1))} символов: {value_image1}", sep='')
    # Добавляем фото
    status, result = pf.change_pet_photo(auth_key, pet_photo, pet_id)
    value_image2 = result.get('pet_photo')  # получаем код image новой фотки
    print(f"value_image2: {len(str(value_image2))} символов: {value_image2}")
    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    # Если полученное значение кода одной картинки не равно значению кода другой картинки - PASSED:
    assert value_image1 != value_image2


"""Тестируем добавление питомца с фото без применения MultipartEncoder и др...ФИЧА-3 и 4. """
def test_add_new_pet_with_photo(name='King-Kong', animal_type='Monkey', age='155', pet_photo=r'../images/king-kong3.jpg'):
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key, _, _ = pf.get_api_key(valid_email, valid_password)
    # Добавляем питомца
    status, result, content, optional, url = pf.add_new_pet_with_photo(auth_key, name, animal_type, age, pet_photo)
    """ФИЧА-5 Вывод полученного ответа в файл. В первом тесте модуля ставим 'w', в последующих 'a'"""
    with open("out_json.json", 'w', encoding='utf8') as my_file:
        my_file.write(f'\n{inspect.currentframe().f_code.co_name}:\n')  # ФИЧА-6 Выводим имя функции, как заголовок ответа
        my_file.write(str(f'\n{status}\n{content}\n{optional}\n{url}\n'))
        json.dump(result, my_file, ensure_ascii=False, indent=4)
    # Сверяем полученный ответ с ожидаемым результатом:
    assert status == 200
    assert result['name'] == name, result['animal_type'] == animal_type and result['age'] == age
    assert 'data:image/jpeg' in result.get('pet_photo')
    assert optional.get('auth_key') == auth_key.get('key')
    assert 'api/pets' in url


"""ФИЧА-7. Тестируем возможность удаления всех питомцев пользователя"""
def test_delete_all_pets():
    # Для запуска нужно в т.ч. добавить запрос на удаление питомца: delete_pet
    # Получаем ключ auth_key и запрашиваем список питомцев пользователя:
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    with open("out_json.json", 'a', encoding='utf8') as my_file:
        my_file.write(f'\n{inspect.currentframe().f_code.co_name}/Текущий список питомцев:\n')
        json.dump(my_pets, my_file, ensure_ascii=False, indent=4)

    pet_id = my_pets['pets'][0]['id']
    # Получаем в цикле id всех питомцев из списка и отправляем запрос на удаление:
    for id_pet in my_pets["pets"]:
        pf.delete_pet(auth_key, id_pet["id"])
    # Ещё раз запрашиваем список питомцев:
    status, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    with open("out_json.json", 'a', encoding='utf8') as my_file:
        my_file.write(f'\n{inspect.currentframe().f_code.co_name}/Список после удаления:\n')
        json.dump(my_pets, my_file, ensure_ascii=False, indent=4)
    assert status == 200
    assert pet_id not in my_pets.values()



"""ФИКСТУРЫ / прописываем их в файле conftest.py (в одной папке с тестами), откуда некоторые из них
будут запускаться автоматически"""

# ФИЧА-8. Фикстура для получения ключа auth_key
# После её назначения, в запросе get_api_key не будет необходимости
@pytest.fixture()
def get_api_key_fix():
    headers = {'email': valid_email, 'password': valid_password}
    res = requests.get("https://petfriends.skillfactory.ru/api/key", headers=headers)
    optional = res.request.headers
    assert optional.get('email') == valid_email
    assert optional.get('password') == valid_password
    assert res.status_code == 200
    try:
        result = res.json()
    except json.decoder.JSONDecodeError:
        result = res.text
    return result


# ФИЧА-9. Фикстура для получения названий выполняемых тестов
# Назначается добавлением перед функций скрипта: @pytest.mark.usefixtures("get_name_func")
@pytest.fixture()
def get_name_func(request):
    print("\nНазвание теста:", request.node.name)
    yield


# ФИЧА-10. Фикстура получения времени обработки каждого теста
# Выполняется автоматически для каждого теста
@pytest.fixture(autouse=True)
def time_delta():
    start_time = time.time_ns()
    yield
    end_time = time.time_ns()
    print(f"\nВремя теста: {(end_time - start_time)//1000000}мс\n")



"""<<<<<< Примеры ТЕСТов для фикстур >>>>>>>"""
@pytest.mark.usefixtures("get_name_func")  # фикстура для вывода в консоли названия теста
def test_get_api_key(get_api_keys):  # в аргументе функции - фикстура для получения ключа
    result = get_api_keys
    # Сверяем полученные данные с нашими ожиданиями
    assert 'key' in result

# >>>Out print:
# Название теста: test_get_api_key
# PASSED [ 10%]
# Время теста: 106мс



"""ФИЧА-11. ПРИМЕР ПРИМЕНЕНИЯ ФИКСТУР ДЛЯ КЛАССА"""

# БЛОК SETUP:
# Фикстура для класса работает в паре с: @pytest.mark.usefixtures("имя фикстуры")
@pytest.fixture()  # если указать scope="class", фикстура исполнится только для первого теста в классе
# Получение названия выполняемого теста
def get_name_func_setup(request):
    print("Название теста из класса:", request.node.name)
    yield


# БЛОК TEARDOWN:
@pytest.fixture(scope="class")
# Получение времени обработки теста для класса
def time_delta_teardown(request):
    start_time = time.time_ns()
    yield
    end_time = time.time_ns()
    print(f"Время теста для класса {request.node.name}: {(end_time - start_time)//1000000}мс")


"""<<<<<< Примеры ТЕСТов для КЛАССОВ >>>>>>>"""
# Указыаем название фикстур для КЛАССА в аргументе глобальной фикстуры через запятую:
@pytest.mark.usefixtures("get_name_func_setup", "time_delta_teardown")
class TestDeletePets:

    """Тестируем возможность удаления одного питомца"""
    def test_delete_first_pet(self, get_api_keys):

    """Тестируем удаление всех питомцев"""
    def test_delete_all_pets(self, get_api_keys):

# >>>Out print:
# >>Название теста из класса: test_delete_first_pet PASSED[90 %]
# Время теста: 763 мс  # действует фикстура time_delta - для каждого теста, в т.ч. в классе
# >>Название теста из класса: test_delete_all_pets PASSED[100 %]
# Время теста: 1192 мс  # действует фикстура time_delta - для каждого теста, в т.ч. в классе
# >>Время теста для класса TestDeletePets: 1957 мс



"""ДЕКОРАТОРЫ / импортируются из файла: conftest.py - в котором они прописываются"""
# ФИЧА-12. Теория:
def do_it_twice(func):  # создаём декоратор
   def wrapper(*args, **kwargs):  # эта функция wrapper выступает, как обёртка/шаблон для декорирования рабочей функции say_word. [*args, **kwargs] - аргументы, которые могут быть в рабочей функции, в данном случае say_word.
       # В тело функции wrapper добавляем нужный код для рабочей функции say_word - т.е. какое-то дополнение,
       # которое нужно применить к работе этой функции, при этом оно не изменит работу кода внутри самой функции say_word.
       for i in range(3):  # в данном случае мы хотим, чтобы функция say_word сработала 3 раза подряд! (или любая другая функция, для которой мы хотим применить этот декоратор)
           func(*args, **kwargs)
   return wrapper

# добавляем наш декоратор перед функцией, которую нужно декорировать (say_word) в виде синтетического сахара,
# т.е. ставим в начале знак @:
@do_it_twice
def say_word(word):  # декорируемая/рабочая функция
# тело декорируемой функции, в которой м.б. прописан любой код. В данном случае функция выводит любое указанное в ней слово.
    print(word)

say_word("Привет!")  # Вызываем нашу рабочую функцию say_word с указанием в аргументе соответствующего значения. В данном случае текста...
# >>>Out print:
# Привет! # Привет! # Привет!


# ФИЧА-12. Создаём декоратор повтора вызова функции n-раз
def do_repeat_it(func):
    def wrapper(get_api_keys):
        for i in range(3):
            func(get_api_keys)
    return wrapper

# Применяем декоратор после импортирования следующим образом:
@do_repeat_it
def test_add_new_pet(get_api_keys, 'и другие параметры')  # декорируемая функция


# ФИЧА-13. Декоратор получения ответа в файл для test_get_all_pets
def add_file_log(func):
    def wrapper(get_api_keys):
        func(get_api_keys)
        headers = {'auth_key': get_api_keys['key']}
        res = requests.get("https://petfriends.skillfactory.ru/api/pets", headers=headers,
                           params={'filter': "my_pets"})
        content = res.headers
        optional = res.request.headers
        body = res.request.body
        cookie = res.cookies
        url = res.request.url
        status = res.status_code
        try:
            result = res.json()
        except json.decoder.JSONDecodeError:
            result = res.text
        with open("my_log.json", 'w', encoding='utf8') as my_file:
            my_file.write(f'\nСтатус: {status}\nЗаголовки1: {content}\nЗаголовки2: {optional}\nТело запроса: '
                          f'{body}\nКуки: {cookie}\n{url}\nТело ответа:\n')
            json.dump(result, my_file, ensure_ascii=False, indent=4)
        assert res.status_code == 200
        return status, result, content, optional

    return wrapper


# Применяем декоратор после импортирования следующим образом:
@add_file_log
def test_get_all_pets(get_api_keys, filter='my_pets'):




