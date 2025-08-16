## 1. Basics 

### 1.1. Getting started

Row
	horizontalArrangement
		Center, End, SpaceBetween, Start, SpaceAround
	verticalAlignment
		 Top, Center, Bottom, CenterVertically
Column
	horizontalAlignment
		End, CenterHorizontally, Start
	verticalArrangement
		Center, Top, SpaceBetween, Bottom, SpaceAround
Box
Modifier
	fillMaxSize
	background(Color.Gray)
	height(60.dp)
	width
	requiredHeight/Width
	padding
	border

// consequent borders/paddings

Text("text", 
	Modifier
	.offset(-5).pd
	.clickable { })

### 1.2 Image Card Composable
@Composable
fun ImageCard() {  //composable function

}

## 2. Tutorial

### 2.1 Composable functions
Composable functions let you define app's UI programmatically by describing how it should look and providing data dependencies

setContent block defines the activity's layout where composable functions are called

@Composable

### 2.2 Layouts
UI elements are hierarchical (elements in other elements). Building UI hierarchy by calling composable functions from other composable functions

data class Message
Column
Row 
Box

Image(painter, contentDescription)

Spacer
Modifiers: .size, .clip, .width, .height

### 2.3 Material Design
Theme, Surface
MaterialTheme.colorScheme.primary/secondary
MaterialTheme.typography.titleSmall/bodyMedium
MaterialTheme.shape

### 2.4 Lists and animations
LazyColumn/Row render only the elements that are visible on screen

To keep track of state change, you have to use functions remember and mutableStateOf
Composable functions can store local state in memory by using remember, and track changes to the value passed to mutableStateOf


## 3
Recomposition - process of regenerating of UI when state changes
@Composable 
fun Survey 

## 4. Codelab Baics

Other **@Composables** can be called within another ones
**Activity** - entry point to an app
**Main activity** - launched when the user opens the app
**Theme** - way to style Composable functions

Background color for @Composable using **Surface**
// color of text changes too
**Modifiers** tell a UI element how to lay out, display or behave withing its parent layout
Best practice: modifier parameter in a @Composable 

**Column, Row, Box**

**State** of the item
**Recomposition** - when, if data changes, compose re-executes @Composables with new data, creating an updated UI
To add internal state to a composable you can use the **mutableStateOf**. Can't just assign mutableStateOf to a variable

	@Composable
	fun Greeting() {
		val expanded = mutableStateOf(false)
	}
		
(recomposition -> call the composable again -> resetting the state to false). 
To preserve state across recompositions we should use **remember**.

State that is read or modified by multiple functions should live in a common ancestor - this process is called **state hoisting** (to hoist - to lift/elevate)
Making state hoistable avoids duplicating state and introducing bugs, helps reuse composables, makes composables easier to test
Making state
**by** saves from typing .value every time
In Comose you don't hide UI elements - you don't add them to the composition
**Callbacks** are functions that are passed as arguments to other functions and get executed when the event occurs. 
By passing a function we're making composable more reusable, protecting state from being mutated by other composables

**LazyColumn** renders only the visible items on screen

**Persisting the onboarding screen state**. Click -> rotate => onboarding shown again. Remember works only as long as the composable is kept in the Composition. rememberSaveable
**Persisting the expanded state of the list items**. Expand list item -> scroll until item is out of view/rotate and back -> item is back to its initial state.

**Animation**: high-level APIs for simple animations to low-level methods for full control and complex transitions.
Any animation created with **animate\*AsState** is interruptible 

Replacing button with an icon: **IconButton**

## Basic layouts in Compose

Analyzing design (reusable components)
**Pixel-perfect way**

Search bar - **TextField**
When writing composables, you use **modifiers** to:
- Change the composable's size, layout, behavior, and appearance.
- Add information, like accessibility labels.
- Process user input.
- Add high-level interactions, like making an element clickable, scrollable, draggable, or zoomable.
**List of modifiers**, **heightIn**