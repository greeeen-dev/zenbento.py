# Bento project example
This is an example of a Zen Rice project which follows uCL standards.

## Files
### bento.json
This file serves as the config file for your project. It tells Bento some details about
your project and what it should package.

### userChrome.css
This is the CSS file that will be used to style Zen Browser. It should serve as a loader
for the "packages" your project has.

### userContent.css
Similar to userChrome.css, but this modifies pages that are loaded in the browser rather
than the browser styles.

### zen-rice/
This is a "package" that is loaded by userChrome.css.

### zen-rice-usercontent/
This is a "package" that is loaded by userContent.css.