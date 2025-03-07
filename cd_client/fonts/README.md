# Custom Font Installation

The `CustomFont.ttf` file in this directory is a placeholder. To use your own custom font:

1. Replace the `CustomFont.ttf` file with your preferred TTF font
2. The font is already configured in `../css/styles.css` with the following code:

```css
@font-face {
  font-family: 'CustomFont';
  src: url('../fonts/CustomFont.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}
```

3. If your font has multiple weights or styles, you can add additional `@font-face` declarations

The font is applied to the entire application as it's set as the primary font in the body element:

```css
body {
  font-family: 'CustomFont', 'Poppins', sans-serif;
  /* other styles... */
}
```

Poppins is used as a fallback in case the custom font fails to load.