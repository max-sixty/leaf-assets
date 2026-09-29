# Leaf assets

Generated image assets for [Leaf](https://github.com/max-sixty/leaf) and
[leaf.page](https://leaf.page/). Leaf pins an exact commit from this repository, so
historical checkouts keep reproducible site inputs without carrying binary history in
the main repository.

Each file sits at the path its reader in Leaf's tree would look for it. The
images under `examples/` are generated and published by Leaf's
`wt refresh-previews` command, and those under `demo/` by `leaf-dev record-demo`;
`examples/media/` holds the images the example pages show, which
`leaf-dev publish-media` adds, and `evals/` what a guidance case hands its child.
Do not edit them by hand.
