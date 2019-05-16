# autodisable-global-shortcuts

This is a simple python app that automatically disables global shorts when a specific window is in focus and re-enables them when it loses focus.

Primary reason I've used this is for the Citrix chrome app which is unable to passthrough global shorts since the DE (include gnome, cinnamon and for those still using it, also unity) intercept it and do not forward it to the application.

The code in here is based on [an answers on askubuntu.com](https://askubuntu.com/questions/862957/block-unity-keyboard-shortcuts-when-a-certain-application-is-active) by the user [Raphael](https://askubuntu.com/users/69674/raphael) which was based on a previous answer.

There are a few bugs I've fixed (e.g. some times it would crash and lose your shortcuts), and I've improved it so it uses xdotool's IDs rather than pids. This is so that it chrome apps can also be differentiated (previous it would see all chrome windows as the same, including chrome apps).

## How to use
First you need to find out how best to identify your window. If `xdotool search` returns the correct pid, then you're golding.

You can use `xprop | grep 'CLASS'` to retrieve the values for `--class` and `--classname` for `xdotool search`. See [this AskUbuntu](https://askubuntu.com/questions/1060170/xdotool-what-are-class-and-classname-for-a-window) for more info.

Once you've figured out the correct arguments for `xdotool search` that return the ID for your window, open the `autodisable-global-shortcuts.py` and change the `xdotool_search_args` variable to contain all the args. The args will be prepended with `xdotool search` and executed.

Finally, update the `shortcuts` variables to include all the shortcuts you want to disable.

Once you've done both, you can run the application without any arguments and leave it running in the background. Then you can do what you need to do.
