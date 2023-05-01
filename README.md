# Leonia Bot

<img src="leonia_bot/leonia.png"
     alt="Leonia bot"
     style="width: 200px;" />

## Introduction

This is a proof of concept for a chat bot developed in Python using
[Flet](https://flet.dev/) as GUI and [Hugging Face](https://huggingface.co/) as
the model provider. The goal is having a desktop application that can be used
to chat with a chat bot using a pretrained model.

In it's current state, the application is not for non-technical users. The
application is not ready for production and it's not recommended to use it for
any purpose other than testing.

I'm learning these libraries as I go, so the code is probably not the best. If
you have any suggestions, please open an issue or a pull request.

## Running the application

After cloning the repository, try this:

```bash
python leonia_bot/leonia_bot.py
```

If you get a message about missing dependencies, install them using `pip`
