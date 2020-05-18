# Spock

:notes: Sync the music playing on Spotify with your Slack status

## Usage

You need to prepare Slack OAuth Access Token and Spotify Client ID, Client Secret, and Redirect URI.

Refer:

- <https://api.slack.com>
- <https://developer.spotify.com>

Note that give `users.profile.write` permission to Slack OAuth Access Token.

After the preparation, set them to the environment variables with reference to [.env.sample](./.env.sample) and run `spock`.

Options are follows:

- `-c`, `--continuous`

  Set next update schedule dynamically.  
  To get the track playing in Spotify you need to hit API.  
  However, you cannot hit API every second, so Spock schedules the time to switch to the next track, which can be calculated from the response.  
  This option is useful for continuous playback without changing the track, but is not recommended if you frequently change the track yourself on Spotify.

- `-e`, `--emoji`

  Emoji for Slack status.  
  By default, this argument is set to `:musical_note:` :musical_note:.  
  You can set custom emojis, for example, you can set a Spotify icon on Slack and set `:spotify:` as this argument.

- `-i`, `--interval`

  Interval (min) to hit API in the normal mode.  
  By default, this argument is set to 3 minutes.  
  If it is not set to `--continuous`, Spock periodically hits API.  
  By setting this argument, you can set the interval of hitting API.

## Install

```sh
pip install git+https://github.com/skmatz/spock.git [--user]
```
