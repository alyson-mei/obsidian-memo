**State** - value that can change over time
States are updated in response to events
**Events** are inputs generated from outside or inside an app

1) count++ without using state => compose won't detect count as a state and won't redraw the screen
2) not using remember => variable count is re-initialized back to 0, so we need to preserve value across recompositions

Compose apps transform data into UI by calling composable functions
**Composition** - description of the UI built by Compose when it executes composables

Compose has a state tracking system that shedules recompositions for any composable that reads particular state

**remember** - composable inline function

```
Column(modifier = modifier.padding(16.dp)) {       
	var count by remember { mutableStateOf(0) }       
	Text("You've had $count glasses.")       
	Button(onClick = { count++ }, Modifier.padding(top = 8.dp)) {           Text("Add one")       
	}  
}
```

Compose - declarative UI framework (how the UI is under specific conditions of state)
Composable function called during the composition => **present** in the composition. Otherwise **absent**

[`remember`](https://developer.android.com/reference/kotlin/androidx/compose/runtime/package-summary#remember(kotlin.Function0)) stores objects in the Composition, and forgets the object if the source location where `remember` is called is not invoked again during a recomposition

Rotation => activity is recreated => state is forgotten
Remember helps to retain state across recompositions but not across config changes. Use **rememberSaveable**