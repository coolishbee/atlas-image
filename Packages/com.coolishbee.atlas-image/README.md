# UI Atlas Image

`AtlasImage` extends `UnityEngine.UI.Image` to display a sprite selected by `SpriteAtlas` and sprite name. The package includes an atlas-specific sprite picker, a border editor, and Image conversion tools.

## Requirements

| Component | Version |
|---|---|
| Unity | `6000.0` or later |
| `com.unity.ugui` | `2.0.0` |
| `com.unity.2d.sprite` | `1.0.0` |

Package ID: `com.coolishbee.atlas-image`. Dependencies are resolved by Unity Package Manager.

## Installation

In Unity Package Manager, select **Install package from git URL** and enter:

```text
https://github.com/coolishbee/atlas-image.git?path=Packages/com.coolishbee.atlas-image#v1.0.0
```

## Project setup

Enable Sprite Atlas V2 in the project's Editor settings. Images may not display correctly in the Editor when sprite packing is disabled.

```text
Edit > Project Settings > Editor > Sprite Packing Mode
Sprite Atlas V2 - Enabled
```

Add the sprites you want to display to a `SpriteAtlas` and give them distinct names.

## Editor tools

| Menu | Action |
|---|---|
| `GameObject/UI/Atlas Image` | Create an AtlasImage object. |
| `GameObject/UI/Button - Atlas Image` | Create a button with an AtlasImage background and TextMeshPro text. |
| `GameObject/UI/Convert Image to AtlasImage` | Convert Images on selected objects to AtlasImages. |
| Image component context menu: `Convert To AtlasImage` | Convert an Image component to AtlasImage. |
| AtlasImage component context menu: `Convert To Image` | Convert an AtlasImage component to Image. |

Assign an atlas in the Inspector, then click the sprite field to open the sprite picker for that atlas.

Use the **Border** control in the preview to edit 9-slice borders. Applying changes updates the source sprite's border values and repacks the atlas.

## Runtime usage

```csharp
using Coolishbee.AtlasImage;
using UnityEngine;

public class AtlasImageController : MonoBehaviour
{
    [SerializeField] private AtlasImage atlasImage;

    public void ShowSprite(string spriteName)
    {
        if (atlasImage != null)
        {
            atlasImage.spriteName = spriteName;
        }
    }
}
```

Assign the atlas through the Inspector or `atlasImage.spriteAtlas`. Set `atlasImage.spriteName` to the name of a sprite in that atlas.

## Sample

Select this package in Package Manager and import **AtlasImage Sample** from its samples list. Open the following scene in the imported sample and use the buttons to switch sprites:

```text
Scenes/AtlasImageSample.unity
```

The repository's `SampleProject/` already contains the same sample and uses Unity `6000.3.18f1`. Do not import the sample again in that project.

## License

[MIT License](LICENSE).
