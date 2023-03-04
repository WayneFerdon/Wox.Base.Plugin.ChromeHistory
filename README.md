<!--
 * @Author: WayneFerdon wayneferdon@hotmail.com
 * @Date: 2023-03-04 12:45:56
 * @LastEditors: WayneFerdon wayneferdon@hotmail.com
 * @LastEditTime: 2023-03-04 23:29:46
 * @FilePath: \Flow.Launcher.Plugin.ChromeHistory\README.md
 * ----------------------------------------------------------------
 * Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
 * Licensed to the .NET Foundation under one or more agreements.
 * The .NET Foundation licenses this file to you under the MIT license.
 * See the LICENSE file in the project root for more information.
-->
# Wox.Plugin.ChromeHistory

1. To Change Platform(current supported: Chrome and Chromium Edge), please chang the value of [ChromeQuery.py: Line19: TargetPlatform](https://github.com/WayneFerdon/Wox.Plugin.ChromeHistory/blob/master/ChromeQuery.py#L19)

2. Other Chromium browser should be available too: by adding the bookmark path manually, or just search TargetPlatform in the main.py to find all codes supporting muti-platform

    >see: [ChromeCache.py: Line139: \_\_setPlatform__(TargetPlatform)](https://github.com/WayneFerdon/Wox.Plugin.ChromeHistory/blob/master/ChromeCache.py#L139)

3. In the Browser Appdata, there should be 3 data file needed for loading the cache: Favicons (website icons), History (historys), Bookmarks (bookmark data). In which History is not needed in this plugin

    > it's for another plugin: [Wox.Plugin.ChromeBookmarks](https://github.com/wayneferdon/Wox.Plugin.ChromeBookmarks)

4. To Change from [Flow Launcher](https://github.com/Flow-Launcher/Flow.Launcher) to [legacy Wox launcher](https://github.com/Wox-launcher/Wox), see [Query.py: Line20](https://github.com/WayneFerdon/Wox.Plugin.SteamGames/blob/master/Query.py#L20) ~ [Query.py: Line42](https://github.com/WayneFerdon/Wox.Plugin.SteamGames/blob/master/Query.py#L42)
