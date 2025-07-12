## 1. Defs
1) Coroutines executed within a thread
2) Coroutines are suspendable
3) They can switch their context (switch thread)

## 2. First coroutine
GlobalScope: coroutine will live as long as app does

	GlobalScope.launch { 
	Log.d(TAG, "${Thread.currentThread().name}") 
	}

delay: will only pause the coroutine and not block the whole thread

	delay(3000L)

## 3. Suspend fun
suspend functions can be called only from another suspend function

	suspend fun doNetworkCall(): {
		delay(3000L)
		return "answer"
	}

in a single coroutine: nwc1 -> nwc2 => 6sec

## 4. Coroutine context
describe in which thread coroutine will be started
**Dispatcher**

	GlobalScope.launch(Dispatchers.Main)

Main (UI operations)
IO (network, data operations)
Default (long running calculations)
Unconfined 
newSingleThreadContext(name = "MyThread")

	val answer = doNetworkCall()
	withContext(Dispatchers.Main) {
		Log.d(TAG, "${Thread.currentThread().name}") 
		Log.d(TAG, "${networkCallAnswer}") 
	}

## 5. runBlocking
blocks main thread
1) when you don't need coroutine behavior but want to call suspend function in the main thread
2) testing with "j unit"

delays shouldn't add up:

	runBlocking {
		launch(Dispatchers.IO) {
			delay(200L)
		}
		launch(Dispatchers.IO) {
			delay(200L)
		}
	}

## 6. Jobs

	val job = GlobalScope.launch(Dispatchers.Default) {
		...
	}
	runBlocking {
		job.join()
	}

job blocks thread until coroutine is finished

	job.cancel()

! cancellation is cooperative; coroutine needs to be set up to be correctly cancelled 

	fun fib(n: Int) {...}
	var job = GlobalScope.launch(Dispatchers.Default) {
		for (i in 30..40) {
			Log.d(TAG, "$i: ${fib(i)}") }
	}
	...
	runBlocking {
		delay(2000L)
		job.cancel()
	}

won't be cancelled this way, should be some time to check for cancellation

	if (isActive) { ...
	}

withTimeout

	withTimeout(3000L) {...}

## 7. Async and await

a) times add up

	GlobalScope.launch {
		val time = measureTimeMillis {
			val answer1 = doNetworkCall()
			val answer2 = doNetworkCall()
		}

b) two coroutines, bad approach, but times don't add up

	val job1 = launch { val answer1 = doNetworkCall() }
	val job2 = launch { val answer2 = doNetworkCall() }
	job1.join()
	job2.join()

c) use async 

	val answer1 = async { doNetworkCall() }
	val answer2 = async { doNetworkCall() }
	Log.d(TAG, "${answer.await()})


// await() -> methods are used to ensure the execution will go further until function is executed completely. \[e.g func1().await()]

## 8. lifecycleScope, viewModelScope

GlobalScope may cause memory leaks 

lifecycleScope:

	lifecycleScope.launch {
		while(true) {
			delay(1000L)
			...
		}
	}

## 9. Coroutines with Firebase Firestore

callback hell

	getUser1 { user1 ->
		getUser2 ->
			getMessages {
				messages -> //chat obj
			}
		}

z