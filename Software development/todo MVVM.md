## 1.1 data layer

\1) todo items

	@Entity 
	data class Todo (...) {...}

\2) dao object, used to access data
how we would like to interact with database: insert, delete, etc. 
	
	interface TodoDao {
		@Isert(onConflict = OnConflictStategy.REPLACE)
		suspend fun insertTodo(todo: Todo)
		@Delete
		suspend fun deleteTodo(todo: Todo)
		@Query(...)
		suspend fun getTodoById(id: Int): Todo?
		@Query(...)
		fun getTodos(): Flow<List<Todo>> //get real time updates
	}

\3) todo database

	@Database(
		entities = [Todo::class], //all the tables we have in our db
		version = 1
	)
	abstract class TodoDatabase: RoomDatabase() {
		abstract val dao: TodoDao
	}

\4) a) repository
the job of the repository is to access all data sources and decide which data it should actually forward to a viewmodel. online api -> we could have a repository that fetches new todos from the api, saves to local as a cache. decide which data to show

	interface TodoRepository {
		suspend fun insertTodo(todo: Todo)
		... //boilerplate for such project; same as dao 
	}

b) implementation of repository

	class TodoRepositoryImpl(
		private val dao: TodoDao
	): TodoRepository {
		override suspend fun insertTodo(todo: Todo) {
			dao.insertTodo(todo)
		}
		...
}

## 1.2 dependency injection
giving an object its instance variables 
private val dao

	@HiltAndroidApp
	class TodoApp: Appliation() //in manifest android:name=".TodoApp"

di package

	//central place where we define how dependencies are created
	@Module 
	@InstallIn(SingletonComponent::class)
	object AppModule { //dependencies, lifetime
		@Provides
		@Singleton
		//constructing new db 
		fun provideTodoDatabase(app: Application): TodoDatabase {
			return Room.databaseBuilder(
			app: Application,
			 TodoDatabase::class.java,
			 "todo.db").build()
		}
		@Provides
		@Singleton
			fun providieTodoRepository(db: TodoDatabase): TodoRepository {
			return TodoRepository(db.dao)
		}
	}

## 2. ViewModel
business logic + state of the specific screen (how ui looks in a given moment)