1、查看 Django 版本 $ python -m django --version
2、创建项目 $ django-admin startproject app
2、创建APP $ python manage.py startapp app01 # app01是app名称
3、运行项目 $ python manage.py runserver [8080] # 如果需要更换端口，修改服务器监听的IP $ python manage.py runserver 0:8080
4、创建一个应用 $ python manage.py startapp polls
4、创建后台用户 $ python manage.py createsuperuser
5、改变模型
    1.编辑 models.py 文件，改变模型
    2.在setting.py 里 INSTALLED_APPS 添加 app01.apps.App01Config
    3.运行 $ python manage.py makemigrations polls 为模型的改变生成迁移文件
    4.运行 $ python manage.py sqlmigrate polls 0001 预览 Django 认为需要执行哪些 SQL 语句
    5.运行 $ python manage.py migrate 来应用数据库迁移
    6.修改 model 更新到数据库
        1.删除该app名字下的migrations下的__init__.py等文件
        2.进入数据库，找到django_migrations的表，删除该app名字的所有记录
        3.执行 5.3 和 5.5
6、API $ python manage.py shell
7、查看 Django 源码的位置命令 $ python -c "import django; print(django.__path__)"
8、model
    AutoField         #An IntegerField that automatically increments according to available IDs
    BigAutoField      #A 64-bit integer, guaranteed to fit numbers from 1 to 9223372036854775807.
    BigIntegerField   #-9223372036854775808 to 9223372036854775807
    BinaryField       #A field to store raw binary data. It only supports bytes assignment
    BooleanField
    CharField
    DateField         #e.g 2019-04-27
    DateTimeField     #e.g 2019-04-27 17:53:21
    DecimalField
    DurationField     #storing periods of time ,e.g [DD] [HH:[MM:]]ss[.uuuuuu]"
    EmailField
    FileField         #存储文件
    FloatField
    ImageField        #Inherits all attributes and methods from FileField, but also validates that the uploaded object is a valid image.
    IntegerField
    GenericIPAddressField #IP地址，支持ipv4
    NullBooleanField      #Like a BooleanField, but allows NULL as one of the options
    PositiveIntegerField  #Like an IntegerField, but must be either positive or zero (0). Values from 0 to 2147483647
    PositiveSmallIntegerField #only allows positive  values from 0 to 32767
    SlugField # A slug is a short label for something, containing only letters, numbers, underscores or hyphens.
    SmallIntegerField
    TextField   #A large text field.
    TimeField   #A time, represented in Python by a datetime.time instance.
    URLField
    UUIDField   #A field for storing universally unique identifiers. Uses Python’s UUID class.

    外键
    ForeignKey  # 外键关联
    ManyToManyField  #多对多
    OneToOneField  # 1对1

    null        #If True, Django will store empty values as NULL in the database. Default is False.
    blank       #If True, the field is allowed to be blank. Default is False.

    db_column   #The name of the database column to use for this field. If this isn’t given, Django will use the field’s name.
    db_index    #If True, a database index will be created for this field.
    default     #The default value for the field. This can be a value or a callable object. If callable it will be called every time a new object is created.
    editable    # django admin中用，后面讲
    help_text   # django admin中用，后面讲
    primary_key # If True, this field is the primary key for the model.
    unique      #If True, this field must be unique throughout the table
    unique_for_date    #Set this to the name of a DateField or DateTimeField to require that this field be unique for the value of the date field. For example, if you have a field title that has unique_for_date="pub_date", then Django wouldn’t allow the entry of two records with the same title and pub_date.

    unique_for_month   #Like unique_for_date, but requires the field to be unique with respect to the month.
    unique_for_year
    verbose_name    #A human-readable name for the field. If the verbose name isn’t given, Django will automatically create it using the field’s attribute name


《机器学习实战》、《统计学习方法》、《机器学习》

