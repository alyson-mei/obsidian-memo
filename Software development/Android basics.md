## 1. Activities

Activity - unit of the app that user interacts with

In Compose 1 activity
MainActivity - entry point

**onCreate**() - user sees nothing
**onStart**() - user sees ui, but can't interact
**onResume**() - user can interact
activity running
**onPause**() - user probably can still see ui -> onResume() or onStop()
**onStop**() - user don't see anything (e.g. minimized) -> onRestart() or App process killed or onDestroy()
**onRestart**() (e.g. opened back) -> onStart()
**onDestroy**() (swiping the app away)

overriding this functions to react

## 2. Tasks, Back Stack, Launch Modes

e.g. in browser app: v 
Browser screen
Bookmark screen
New bookmark screen

Task represents collection of multiple screen/activities that are run together (they form backstack)

Launch mode allows to set a behavior when activity is pushed to a backstack
**Standart** (new activity pushed to a backstack)
**Single top** (e.g. send user to already existing activity)
**Single Task** (new instances will be launched in a completely different tasks  )
**Single tasks** (isolated tasks)

## 3. ViewModels & Configuration changes

	class ContactsViewModel {
		var backgroundColor by mutableStateOf(Color.White)
			private set
		fun changeBackgroundColor() {
			backgroundColor = Color.Red
		}
	}
	...
	class MainActivity(...)
		private val viewModel = ContactsViewModel()
		Surface(color = viewModel.backgroundColor) { 
			Button(onClick = {
				viewModel.changeBackgroundColor}) {Text("change color")} 
			}

config change => activity recreates

fix:
1) ContactsViewModel: ViewModel()
 private val viewModel by viewModel\<ContactsViewModel>()
2) lifecycle dependency
-//- and in the theme scope
	val viewModel = viewModel\<...>()

add constructor => need factory 

	val viewModel = viewModel<CVM>(
		factory = object : ViewModelProvider.Factory {
			override fun <T : ViewModel> create(modelClass: Class<T>): T {
			return ContactsViewModel(
				helloWorld = "Hello world!"
			) as T
		}
	})