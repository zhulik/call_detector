# call_detector

_call_detector_ listens to microphone and camera states to detect if the user is participating in an online call.
Publishes gathered information to an MQTT broker.

## Where it works

It works only on linux(at the current moment). I don't have plans to add support for other operating systems.

## How it works

_call_detector_ listens to pulseadio events to detect the app which uses the microphone and uses inotify with
some /proc magic to detect the app which uses the camera.

## MQTT

_call_detector_ was only tested against [mosquitto](https://mosquitto.org/) MQTT broker with login/password authentication and TLS enabled, however in therory it can work without TLS and authentication and agains any broker supported by
[gmqtt](https://github.com/wialon/gmqtt).

Every time the _call_detector_ detects a new camera or microphone user it publishes a message to a topic named like
`call_detector/<hostname>` where hostname is the hostname of the machine where you run _call_detector_. Also it sends a message
on start and every minute.

Message examples:

`{"camera": [], "microphone": [], "call": true}` when camera and microphone are not active.

`{"camera": ["firefox"], "microphone": ["firefox"], "call": false}` when user is in an online call using firefox.

## Usage

Basic usage:

`call_detector -H mqtt.example.com -U user -P password`

More advanced options can be found in `help`

`call_detector --help`

## Home Assistant

Binary sensor:

```yaml
binary_sensor:
  - platform: mqtt
    name: "User in an online meeting"
    state_topic: "call_detector/<hostname>" # check call_detector --help to find the default topic for your computer
    value_template: "{{ 'ON' if value_json.call else 'OFF' }}"
    json_attributes_topic: "call_detector/<hostname>" # same as state_topic
    json_attributes_template: "{{ value_json | tojson }}"
```

Automation example:

```yaml
- alias: Pause music while User is in an online meting
  trigger:
    - platform: state
      entity_id: binary_sensor.user_in_an_online_meeting
      to: "on"

  condition:
    - condition: state
      entity_id: media_player.mpd
      state: "playing"

  action:
    - service: media_player.media_pause
      data:
        entity_id: media_player.mpd

    - wait_for_trigger:
        - platform: state
          entity_id: binary_sensor.user_in_an_online_meeting
          to: "off"

    - service: media_player.media_play
      data:
        entity_id: media_player.mpd
```

## Contribution

You know;)
