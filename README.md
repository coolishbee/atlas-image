# UI Atlas Image

A Unity uGUI component that displays sprites from a `SpriteAtlas` by name, with an atlas-specific sprite picker, a border editor, and Image conversion tools.

## Features

- Select images using a `SpriteAtlas` and sprite name.
- Switch sprites by name at runtime.
- Browse sprites from the selected atlas in the Inspector.
- Edit sprite borders for 9-slice images.
- Convert between `Image` and `AtlasImage`, including bulk conversion of selected objects.

## Requirements

- Unity `6000.0` or later
- `com.unity.ugui` `2.0.0`
- `com.unity.2d.sprite` `1.0.0`

Package dependencies are declared in `package.json` and resolved by Unity Package Manager.

## Installation

In Unity Package Manager, select **Install package from git URL** and enter:

```text
https://github.com/coolishbee/atlas-image.git?path=Packages/com.coolishbee.atlas-image#v1.0.0
```

## Getting started

Enable **Sprite Atlas V2** in the project's Editor settings. Add an `AtlasImage` component, assign an atlas, and select a sprite in the Inspector.

See the [package README](Packages/com.coolishbee.atlas-image/README.md) for setup instructions, editor tools, and code examples.

## Repository layout

| Path | Purpose |
|---|---|
| `Packages/com.coolishbee.atlas-image/` | UPM package |
| `SampleProject/` | Unity project using the local package |

To explore the sample, open `SampleProject/` with Unity `6000.3.18f1` and run:

```text
Assets/AtlasImageSample/Scenes/AtlasImageSample.unity
```

The sample is already included in this project. Do not import it again through Package Manager.

## License

[MIT License](Packages/com.coolishbee.atlas-image/LICENSE).
