Addon to show every card's first review of each day on Anki's deck congratulations screen.

Cards go down, days go from right to left. You can hover a square to see the date. And you can click the square to go to the card in Deck Browser.

![Screenshot](docs/Screenshot_01.png?raw=true)

### Installation

https://ankiweb.net/shared/info/556289348

To download this add-on, please copy and paste the following code into Anki:

    556289348

### Configuration

You can change sizes and limits and many other options using Anki's Config button inside Add-ons list.

- `box_width` - each box width (default: `4`)
- `box_height` - each box height (default: `4`)
- `card_limit` - number of cards to show, or `-1` to show all (default: `-1`)
- `due_days` - number of days to add to the left of image to show due cards (default: `7`)
- `image_height` - size of the image block inside anki interface in html format (default: `"450px"`)
- `order_by` - cards order, can be one of `min_date`, `max_date`, `due_date` or mix (default: `"min_date, due_date"`)
- `order_reverse` - reverse order direction, can be `true` or `false` (default: `true`)
- `show_line` - show separator before due days (default: `true`)

### Changelog

- **v0.8** Due cards and configurable cards order
- **v0.7** Added to Overview screen
- **v0.6** Subdecks support
- **v0.5** Max date fix
- **v0.4** Configurable sizes and limits
- **v0.3** Empty decks handling
- **v0.2** Added buried and suspended cards
- **v0.1** Initial Release
