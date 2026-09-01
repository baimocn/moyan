# Chapter 1: Basic Prompt Structure

- [Lesson](#lesson)
- [Exercises](#exercises)
- [Example Playground](#example-playground)

## Setup

Run the following setup cell to load your API key and establish the `get_completion` helper function.


```python
!pip install anthropic

# Import python's built-in regular expression library
import re
import anthropic

# Retrieve the API_KEY & MODEL_NAME variables from the IPython store
%store -r API_KEY
%store -r MODEL_NAME

client = anthropic.Anthropic(api_key=API_KEY)

def get_completion(prompt: str, system_prompt=""):
    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2000,
        temperature=0.0,
        system=system_prompt,
        messages=[
          {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text
```


---

## Lesson

Anthropic offers two APIs, the legacy [Text Completions API](https://docs.anthropic.com/claude/reference/complete_post) and the current [Messages API](https://docs.anthropic.com/claude/reference/messages_post). For this tutorial, we will be exclusively using the Messages API.

At minimum, a call to Claude using the Messages API requires the following parameters:
- `model`: the [API model name](https://docs.anthropic.com/claude/docs/models-overview#model-recommendations) of the model that you intend to call

- `max_tokens`: the maximum number of tokens to generate before stopping. Note that Claude may stop before reaching this maximum. This parameter only specifies the absolute maximum number of tokens to generate. Furthermore, this is a *hard* stop, meaning that it may cause Claude to stop generating mid-word or mid-sentence.

- `messages`: an array of input messages. Our models are trained to operate on alternating `user` and `assistant` conversational turns. When creating a new `Message`, you specify the prior conversational turns with the messages parameter, and the model then generates the next `Message` in the conversation.
  - Each input message must be an object with a `role` and `content`. You can specify a single `user`-role message, or you can include multiple `user` and `assistant` messages (they must alternate, if so). The first message must always use the user `role`.

There are also optional parameters, such as:
- `system`: the system prompt - more on this below.
  
- `temperature`: the degree of variability in Claude's response. For these lessons and exercises, we have set `temperature` to 0.

For a complete list of all API parameters, visit our [API documentation](https://docs.anthropic.com/claude/reference/messages_post).


### Examples

Let's take a look at how Claude responds to some correctly-formatted prompts. For each of the following cells, run the cell (`shift+enter`), and Claude's response will appear below the block.


```python
# Prompt
PROMPT = "Hi Claude, how are you?"

# Print Claude's response
print(get_completion(PROMPT))
```


```python
# Prompt
PROMPT = "Can you tell me the color of the ocean?"

# Print Claude's response
print(get_completion(PROMPT))
```


```python
# Prompt
PROMPT = "What year was Celine Dion born in?"

# Print Claude's response
print(get_completion(PROMPT))
```


Now let's take a look at some prompts that do not include the correct Messages API formatting. For these malformatted prompts, the Messages API returns an error.

First, we have an example of a Messages API call that lacks `role` and `content` fields in the `messages` array.


```python
# Get Claude's response
response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2000,
        temperature=0.0,
        messages=[
          {"Hi Claude, how are you?"}
        ]
    )

# Print Claude's response
print(response[0].text)
```


Here's a prompt that fails to alternate between the `user` and `assistant` roles.


```python
# Get Claude's response
response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2000,
        temperature=0.0,
        messages=[
          {"role": "user", "content": "What year was Celine Dion born in?"},
          {"role": "user", "content": "Also, can you tell me some other facts about her?"}
        ]
    )

# Print Claude's response
print(response[0].text)
```


`user` and `assistant` messages **MUST alternate**, and messages **MUST start with a `user` turn**. You can have multiple `user` & `assistant` pairs in a prompt (as if simulating a multi-turn conversation). You can also put words into a terminal `assistant` message for Claude to continue from where you left off (more on that in later chapters).

#### System Prompts

You can also use **system prompts**. A system prompt is a way to **provide context, instructions, and guidelines to Claude** before presenting it with a question or task in the "User" turn. 

Structurally, system prompts exist separately from the list of `user` & `assistant` messages, and thus belong in a separate `system` parameter (take a look at the structure of the `get_completion` helper function in the [Setup](#setup) section of the notebook). 

Within this tutorial, wherever we might utilize a system prompt, we have provided you a `system` field in your completions function. Should you not want to use a system prompt, simply set the `SYSTEM_PROMPT` variable to an empty string.


#### System Prompt Example


```python
# System prompt
SYSTEM_PROMPT = "Your answer should always be a series of critical thinking questions that further the conversation (do not provide answers to your questions). Do not actually answer the user question."

# Prompt
PROMPT = "Why is the sky blue?"

# Print Claude's response
print(get_completion(PROMPT, SYSTEM_PROMPT))
```


Why use a system prompt? A **well-written system prompt can improve Claude's performance** in a variety of ways, such as increasing Claude's ability to follow rules and instructions. For more information, visit our documentation on [how to use system prompts](https://docs.anthropic.com/claude/docs/how-to-use-system-prompts) with Claude.

Now we'll dive into some exercises. If you would like to experiment with the lesson prompts without changing any content above, scroll all the way to the bottom of the lesson notebook to visit the [**Example Playground**](#example-playground).


---

## Exercises
- [Exercise 1.1 - Counting to Three](#exercise-11---counting-to-three)
- [Exercise 1.2 - System Prompt](#exercise-12---system-prompt)


### Exercise 1.1 - Counting to Three
Using proper `user` / `assistant` formatting, edit the `PROMPT` below to get Claude to **count to three.** The output will also indicate whether your solution is correct.


```python
# Prompt - this is the only field you should change
PROMPT = "[Replace this text]"

# Get Claude's response
response = get_completion(PROMPT)

# Function to grade exercise correctness
def grade_exercise(text):
    pattern = re.compile(r'^(?=.*1)(?=.*2)(?=.*3).*$', re.DOTALL)
    return bool(pattern.match(text))

# Print Claude's response and the corresponding grade
print(response)
print("\n--------------------------- GRADING ---------------------------")
print("This exercise has been correctly solved:", grade_exercise(response))
```


❓ If you want a hint, run the cell below!


```python
from hints import exercise_1_1_hint; print(exercise_1_1_hint)
```


### Exercise 1.2 - System Prompt

Modify the `SYSTEM_PROMPT` to make Claude respond like it's a 3 year old child.


```python
# System prompt - this is the only field you should change
SYSTEM_PROMPT = "[Replace this text]"

# Prompt
PROMPT = "How big is the sky?"

# Get Claude's response
response = get_completion(PROMPT, SYSTEM_PROMPT)

# Function to grade exercise correctness
def grade_exercise(text):
    return bool(re.search(r"giggles", text) or re.search(r"soo", text))

# Print Claude's response and the corresponding grade
print(response)
print("\n--------------------------- GRADING ---------------------------")
print("This exercise has been correctly solved:", grade_exercise(response))
```


❓ If you want a hint, run the cell below!


```python
from hints import exercise_1_2_hint; print(exercise_1_2_hint)
```


### Congrats!

If you've solved all exercises up until this point, you're ready to move to the next chapter. Happy prompting!


---

## Example Playground

This is an area for you to experiment freely with the prompt examples shown in this lesson and tweak prompts to see how it may affect Claude's responses.


```python
# Prompt
PROMPT = "Hi Claude, how are you?"

# Print Claude's response
print(get_completion(PROMPT))
```


```python
# Prompt
PROMPT = "Can you tell me the color of the ocean?"

# Print Claude's response
print(get_completion(PROMPT))
```


```python
# Prompt
PROMPT = "What year was Celine Dion born in?"

# Print Claude's response
print(get_completion(PROMPT))
```


```python
# Get Claude's response
response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2000,
        temperature=0.0,
        messages=[
          {"Hi Claude, how are you?"}
        ]
    )

# Print Claude's response
print(response[0].text)
```


```python
# Get Claude's response
response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2000,
        temperature=0.0,
        messages=[
          {"role": "user", "content": "What year was Celine Dion born in?"},
          {"role": "user", "content": "Also, can you tell me some other facts about her?"}
        ]
    )

# Print Claude's response
print(response[0].text)
```


```python
# System prompt
SYSTEM_PROMPT = "Your answer should always be a series of critical thinking questions that further the conversation (do not provide answers to your questions). Do not actually answer the user question."

# Prompt
PROMPT = "Why is the sky blue?"

# Print Claude's response
print(get_completion(PROMPT, SYSTEM_PROMPT))
```
