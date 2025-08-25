## 1. Overview
	## 2. UI layer

UI is a visual representation of the application state as retrieved from the data layer
The **UI layer** is the pipeline that converts application data changes to a form that the UI can present and then displays it

Role: 
1. Consume app data, transform into data the UI can easily render
2. Consume UI-renderable data and transform it into UI elements
3. Consume user input events and reflect effects in the UI data as needed
4. Repeat 1..3

UI elements + UI state (what app says user should see) = UI (what user sees)

Info required to fully render the UI can be encapsulated in a NewsUiState dc:

	data class NewsUiState(
		val isSignedIn:Boolean = false,
		val isPremium: Boolean = false,
		val newsItems: List<NewsItemUiState> = listOf(),
		val userMessages: List<Message> = listOf()
	)
	data class NewsItemUiState(
		val title: String,
		val body: String,
		val bookmarked: Boolean = false,
		...)

### Immutability
Frees up the UI to focus on a single role: to read the state and update its UI elements accordingly. e.g.: if the bookmarked flag was updated in the Activity class, that flag would be competing with the data layer as the source of the bookmarked status of an article
### Naming
functionality + UiState
### UDF
The patter there the state flows down and the events flow up
#### State holders
Classes that are resonsible for the production of UI state and contain the necessary logic for that task
ViewModel

- The ViewModel holds and exposes the state to be consumed by the UI. The UI state is application data transformed by the ViewModel
- The UI notifies the ViewModel of user events
- The ViewModel handles the user actions and updates the state
- The updated state is fed back to the UI to render
- repeat for every event that causes a mutation of state

### Types of logic
- **Business logic** is the implementation of product requirements for app data, placed in domain or data layers
- **UI behavior logic / UI logic** is how to display state changes, should live in UI

### Expose UI state
Observable data holder like LiveData or StareFlow. Have latest states of the UI state cached

	class NewsViewModel(
		private val repository: NewsRepository,
		...
	) : ViewModel() {
		var uiState by mutableStateOf(NewsUiState())
			private set
		private var fetchJob: Job? = null
		fun fetchArticles(category: String) {
			fetchJob?.cancel()
			fetchJob = viewModelScope.launch {
				try {
					val newsItems = repository.newsItemsForCategory(category)
						uiState = uiState.copy(newsItems = newsItems)
				} catch (ioe: IOException) {
					val messages = getMessagesFromThrowable(ioe)
					uiState = uiState.copy(userMessages = messages)
				}
			}
		}
	}

