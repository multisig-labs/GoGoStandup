# GoGoStandup

This is Multisig Labs' official standup bot! 

## Usage

Add the bot [here](https://discord.com/oauth2/authorize?client_id=1014992422054400000&scope=bot&permissions=3072).

Using GoGoStandup is really simple! 

### Standup

Here is how you create a new standup in a channel with `/standup` !

![Standup Command](https://i.ibb.co/MMStZ2n/image.png)

The `message_time` is by default in UTC 24 hour time, and should be in the same format specified in the screenshot. For example, if you wanted a standup notification at 9:00 UTC, you would type `9h` . If you wanted a standup notification at 12:30 UTC, you would type `12h30m` .

But if you're a human, and hopefully you are, you don't think in UTC! You think in your local timezone. Lucky, we support shifting based on the timezone you live in! We support any of the [tz database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) timezones!

![Standup Command with TZ](https://i.ibb.co/tMMQWRJ/image.png)

Finally, if you are the type to have 4 day workweeks, you can specify what days to get reminded on! All you have to do is add a comma-separated list of days of the week ( `["m", "t", "w", "th", "f", "s", "su"]` ) to the `days` field!

![Standup command with days](https://i.ibb.co/qn96zfK/image.png)

And of course, you can always use both `days` and `time_zone` in your standup request!

### Sitdown

If you no longer want to receive standup notifications for a channel, all you have to do is run `/sitdown` !

![Sitdown](https://i.ibb.co/s2NYvmM/image.png)

### Next and Last

If you want to know the last time you gave a standup, just run `/last` .

If you want to know when your next standup is, just run `/next` .

![next](https://i.ibb.co/KLj7hX0/image.png)

And that's it!
