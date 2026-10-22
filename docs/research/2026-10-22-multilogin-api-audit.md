# Multilogin API — nghiên cứu collection

Ngày: 2026-10-22. Nguồn: Postman CLI 1.76.0, `collection get ... --json`.
Workspace: `fcb8367c-8eb4-4173-a511-2e151812fba7` (Ubuntu Postman Web, team).
Collection: `46206122-78bf4173-0a22-4651-890d-b160177d47b1`.
Đây là bằng chứng từ contract và saved examples; chưa gọi API Multilogin thật. Không lưu header Authorization hay giá trị credential từ examples.

## Phạm vi

| Nhóm | Số request |
|---|---:|
| Launcher | 18 |
| Profile Access Management | 15 |
| Profile Management | 20 |
| Browser Profile Data | 1 |
| Proxy | 3 |
| Pre-made Cookies | 4 |
| Script Runner | 4 |
| Profile Import/Export | 6 |
| Object Storage | 16 |
| Bookmark Management | 3 |
| 2FA | 9 |
| Mobile Profile Management | 26 |

Tổng: 125 request. Request trùng đường dẫn vẫn giữ riêng theo ID để audit coverage.

## Những điểm ảnh hưởng thiết kế

- Cloud API: `https://api.multilogin.com`; Launcher: `https://launcher.mlx.yt:45001`; cookies: `https://cookies.multilogin.com`. Có 8 request dùng `{{baseUrl}}`: chưa đọc global value, cần xác nhận mapping trước thực thi.
- Có 37 request URL Launcher, 76 Cloud, 4 cookies và 8 URL biến. Phân loại theo URL, không theo tên folder.
- 75 body kiểu json, 5 text, 2 multipart/form-data, 43 không body. Nhiều body là template chứa placeholder/comment, không parse thành JSON hợp lệ trực tiếp.
- Disabled queryParams thường đóng vai trò tài liệu cho body; không gửi tất cả thành query.
- GET có side effect: start/stop profile, generate token, delete/restore object, group get_or_create; retry cần allowlist theo operation.
- Quick v3 proxy nằm trong parameters; partial update proxy nằm top-level. Không dùng một serializer chung cho mọi operation.
- Start Browser Profile v2 có data.port dạng chuỗi; Script Runner dùng start v1 và trả port trong status.message.
- Stealthfox chỉ hỗ trợ Selenium theo tài liệu start; Mimic hỗ trợ Selenium/Puppeteer/Playwright. custom_start_urls của Mimic có hạn chế khi truyền automation.
- Profile Search dùng limit 1–100, offset 0–10000; mobile list dùng page/page_size. Không giả định cùng pagination hoặc đọc vô hạn được toàn bộ browser profile.
- ISP proxy: host phải có mặt dù rỗng; times=1 khi tạo; proxy đã gán có thể trả 409.
- Partial update có thể bật lại auto_update_core nếu bỏ trường; SDK cần nêu rõ hành vi, không hứa bảo toàn giá trị bị bỏ.
- Mobile IDs là chuỗi số, không phải UUID. ADB set/info tối đa 50 IDs; batch có thể thành công một phần. Mobile statuses: 0 started, 1 starting, 2 idle, 3 expired.
- Mobile upload và validate import dùng multipart. Validate trả validation_id nhưng collection không có import-confirm operation.
- Cloud to Local và Local to Cloud cùng trỏ local_to_cloud: chưa đủ căn cứ triển khai chiều cloud_to_local.
- Nhiều saved examples có HTTP code khác status.http_code; một số object examples chứa http_code=0 và placeholder. Không coi các mẫu này là dữ liệu runtime đã được kiểm chứng.

## Chi tiết từng request

### Launcher / Start Browser Profile

ID: `46206122-cb25cc30-6432-4867-a58a-4d97c43107da`

`GET https://launcher.mlx.yt:45001/api/v2/profile/f/:folder_id/p/:profile_id/start?automation_type=selenium, puppeteer, playwright&headless_mode=false,true`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Start a browser profile.

The endpoint will return a port for automation in the response message if the automation type parameter is passed. See `automation_type` in the "Query Params" section.

**NB: Mimic profiles will work with** **`custom_start_urls`** **only if** **`automation_type`** **is NOT specified. This is to be fixed soon.****Stealthfox profiles work as expected.**

**Required parameters for Strict mode:**

``` json
"folder_id":"<string>",
"profile_id":"<string>",
"automation_type":"<value>",
"headless_mode":<boolean>

 ```

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| folder_id | False | `Required`. Specify the ID of the folder where the profile to launch is stored. Defaults to `default folder`. |
| profile_id | False | `Required`. Specify the ID of the profile to launch. |

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| automation_type | False | `Optional`. Specify the automation type. Mimic can work with any of the types. Stealthfox can only work with **selenium**. Defaults to `selenium`. |
| headless_mode | False | `Optional`. Enable headless mode for all browsers. Defaults to `false`. |

Saved example: Profile Started — HTTP 200
Top-level response keys: data, status
Data keys: browser_type, core_version, id, is_quick, port
Envelope http_code: 200

### Launcher / Start Quick Profile v3

ID: `46206122-043aebc6-6128-427a-87c1-7cbbccde81aa`

`POST https://launcher.mlx.yt:45001/api/v3/profile/quick`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Create a one-time quick browser profile, that opens up after the call is successfully made. Browsing activity and its related data is not saved after the profle has been stopped.

Fingerprint parameters need providing only if flags set to `Custom`.

Check out **Params** to see what each key-value pair is about. To copy the example request body, navigate to **Body**.

Note that the custom URL feature will be available for Mimic quick browsers **ONLY** if the `automation` value is not provided in the request. Stealthfox browsers works as expected.

If you would like to avoid having your profiles updated to the latest available core, specify `auto_update_core` (`true` or `false`) and a specific `core_version`.  
Updating existing profiles to a specific core version is not supported.

**Mimic quick profiles will work with** **`custom_start_urls`** **only if** **`automation_type`** **is NOT specified. This is to be fixed soon. Stealthfox profiles work as expected.**

**NB: It is recommended to use the default values, which keep your browser cores up-to-date. Multilogin does not bear any responsability for ban or detection-related issues if profiles have a dated core version.**

**Required parameters for Strict mode:**

Start Quick Profile v3 has `proxy` inside `parameters`.

``` json
{
    "browser_type": "<string>",
    "os_type": "<string>",
    "automation": "<string>",
    "auto_update_core": <boolean>,
    "core_version": <number>,
    "is_headless": <boolean>,
    "parameters": {
        "flags": {
            "audio_masking": "value",
            "fonts_masking": "value",
            "geolocation_masking": "value",
            "geolocation_popup": "value",
            "graphics_masking": "value",
            "graphics_noise": "value",
            "localization_masking": "value",
            "media_devices_masking": "value",
            "navigator_masking": "value",
            "ports_masking": "value",
            "proxy_masking": "value",
            "screen_masking": "value",
            "timezone_masking": "value",
            "webrtc_masking": "value",
            "canvas_noise" :"value",
            "startup_behavior" :"value"
        }
        "fingerprint": {}
}

 ```

The number of parameters in `fingerprint` may vary depending on the flag values passed in the request body.

To use quick profiles with [Script Runner](https://go.postman.co/workspace/My-Workspace~ccd73442-99e9-4b09-8bed-73dcedfe74b9/documentation/28533318-54a9773a-031e-4904-b607-e372445dc2ba?entity=folder-ae883a9a-6cc8-4de6-bdab-0ce3b05e83a6), use the following additional parameters:

``` json
"automation": "selenium",
"script_file": "your_file.py"

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| browser_type | True | `Required`. Choose the browser type. Note: For `android` only mimic is supported! Defaults to `mimic`, |
| core_version | True | `Optional`. You can skip specifying the value since your profiles will be updated to the latest core each time it is launched. Defaults to `latest`. Cannot specify the version that is 6 versions older then the current latest one. |
| core_minor_version | True | `Optional`. Specify the minor version based on its availability. |
| os_type | True | `Required`. Specify the OS. Defaults to `windows`. |
| script_file | True | `Optional` |
| automation | True | `Optional`. `selenium` only for working with Script Runner. Defaults to `selenium`. |
| is_headless | True | `Optional`. Enable headless mode. Defaults to `false`. |
| proxy | True | `Optional` for `parameters`. Add a proxy to your profiles. |
| save_traffic | True | `Optional` for `proxy`. `false` is set by default. When set to `true`,  disables the loading of images/videos saving the proxy traffic. |
| parameters | True | `Required`. Specify parameters for your profiles. `flags`, `fingerprints`, `storage` **are required** for **parameters**. |
| flags | True | `Required`. Specify flags for your profiles. `webrtc_masking, proxy_masking, geolocation_popup, audio_masking, graphics_noise, ports_masking, navigator_masking, localization_masking, timezone_masking, graphics_masking, fonts_masking, media_devices_masking, screen_masking, geolocation_masking` **are required** for **parameters**. |
| webrtc_masking | True | `Required` for `flags`. Defaults to `mask`. |
| geolocation_popup | True | `Required` for `flags`. Defaults to `prompt`. |
| audio_masking, graphics_noise | True | `Required` for `flags`. Defaults to `mask` for graphic_noise and to `natural` for audio masking. |
| proxy_masking | True | `Required` for `flags`. Defaults to `disabled` unsell proxy is provided, than defaults to `custom`. |
| navigator_masking, localization_masking, timezone_masking, graphics_masking, fonts_masking, media_devices_masking, screen_masking, ports_masking | True | `Required` for `flags`. Defaults to `mask` and for media_devices_masking defaults to `natural`. |
| geolocation_masking | True | `Required` for `flags`. Defaults to `mask`. |
| canvas_noise | True | `Optional` for`flags`. The value is set based on the value of `graphics_noise` by default. To set a specific value for `canvas_noise`, include `canvas_noise` in your request body. Defaults to `mask`. |
| startup_behavior | True | `Optional` for `flags`. `recover` is set by default and allows opening profiles with the tabs from the last session. `custom` opens up profiles with provided custom pages in `custom_start_urls`. Defaults to `recover`. |
| fingerprint | True | `Required` for `parameters`. Specify fingerprints of your profiles if flags are set to `Custom`. Defaults to `optional` unless custom is set. |
| hardware_concurrency | True | `Required` for `navigator`. Specify the value for `hardware_concurrency` if the flag is `Custom`. |
| user_agent | True | `Required` for `navigator`. Specify the value for `user-agent`. |
| platform | True | `Required` for `navigator`. Specify the value for `platform` if the flag is `Custom`. |
| os_cpu | True | `Oprtional` for `navigator`. Specify the value for `os_cpu`if the flag is `Custom`. |
| accept_languages | True | `Required` for `localization`. Specify the value for `accept_languages` if the flag is `Custom`. |
| languages | True | `Required` for `localization`. Pass an empty string. |
| locale | True | `Required` for `localization`. Pass an empty string. |
| zone | True | `Required` for `timezone`.  Specify the value for `zone`. |
| vendor | True | `Required` for `graphic`. Specify the value for `vendor` if the flag is `Custom`. |
| renderer | True | `Required` for `graphic`. Specify the value for `renderer` if the flag is `Custom`. |
| vendor_id | True | `Optional` for `graphic`. Specify the value for `vendor_id` if the flag is `Custom`. |
| renderer_id | True | `Optional` for `graphic`. Specify the value for `renderer_id` if the flag is `Custom`. |
| public_ip | True | `Required` for `webrtc`. Specify the value for `public_ip` if the flag is `Custom`. |
| audio_outputs | True | `Required` for `media_devices`. Specify the value for `audio_outputs` if the flag is `Custom`. |
| video_inputs | True | `Required` for `media_devices`. Specify the value for `video_inputs` if the flag is `Custom`. |
| audio_inputs | True | `Required` for `media_devices`. Specify the value for `audio_inputs` if the flag is `Custom`. |
| width | True | `Required` for `screen`. Specify the value for `width` if the flag is `Custom`. |
| height | True | `Required` for `screen`.  Specify the value for `height` if the flag is `Custom`. |
| pixel_ratio | True | `Required` for `screen`. Specify the value for `pixel_ratio` if the flag is `Custom`. |
| ports | True | `Optional`. Specify the value for `ports` if the flag is `Custom`. |
| accuracy | True | `Required` for `geolocation`. Specify the value for `accuracy` if the flag is `Custom`. |
| altitude | True | `Required` for `geolocation`. Specify the value for `altitude` if the flag is `Custom`. |
| longitude | True | `Required` for `geolocation`. Specify the value for `longitude` if the flag is `Custom`. |
| latitude | True | `Required` for `geolocation`. Specify the value for `latitude` if the flag is `Custom`. |
| fonts | True | `Optional` for `fingerprints`. Specify the value for `fonts` if the flag is `Custom`. |
| cmd_params | True | `Optional` for `fingerprints`. Specify command line parameters for browsers. |
| custom_start_urls | True | `Optional`. Specify custom URLs. Max amount is 5. Defaults to `optional` unselss custom is set. |
| max_touch_points | True | `Optional` for `fingerprint` with `android` os. Default is 5. |

**Body template** (`text`; chưa phải payload runnable):

```text
{
    "browser_type": "<string>",
    "os_type": "<string>",
    "script_file": "<string>",
    "automation": "<string>",
    "core_version": <integer>,
    "core_minor_version": <integer>,
    "is_headless": <boolean>,
    "parameters": {
        "flags": {
            "audio_masking": "<string>",
            "fonts_masking": "<string>",
            "geolocation_masking": "<string>",
            "geolocation_popup": "<string>",
            "graphics_masking": "<string>",
            "graphics_noise": "<string>",
            "localization_masking": "<string>",
            "media_devices_masking": "<string>",
            "navigator_masking": "<string>",
            "ports_masking": "<string>",
            "proxy_masking": "<string>",
            "screen_masking": "<string>",
            "timezone_masking": "<string>",
            "webrtc_masking": "<string>",
            "canvas_noise:": "<string>",
            "startup_behavior": "<string>"
        },
        "proxy": {
            "host": "<string>",
            "type": "<string>",
            "port": <integer>,
            "username": "<string>",
            "password": "<string>"
        },
        "fingerprint": {
            "navigator": {
                "hardware_concurrency": <integer>,
                "platform": "<string>",
                "user_agent": "<string>",
                "os_cpu": "<string>"
            },
            "localization": {
                "languages": "<string>",
                "locale": "<string>",
                "accept_languages": "<string>"
            },
            "timezone": {
                "zone": "<string>"
            },
            "graphic": {
                "renderer": "<string>",
                "vendor": "<string>"
            },
            "webrtc": {
                "public_ip": "<string>"
            },
            "media_devices": {
                "audio_inputs": <integer>,
                "audio_outputs": <integer>,
                "video_inputs": <integer>
            },
            "screen": {
                "height": <integer>,
                "pixel_ratio": <double>,
                "width": <integer>
            },
            "geolocation": {
                "accuracy": <number>,
                "altitude": <number>,
                "latitude": <number>,
                "longitude": <number>
            },
            "ports": [
                <integer>,
            ],
            "fonts": [
                "<string>"
            ],
            "cmd_params": {
                "params": [
                    {
                        "flag": "<string>",
                        "value": "<boolean>"
                    }
                ]
            }
        },
        "custom_start_urls": [
            "<string>"
        ]
    }
}
```

Saved example: Quick Profile v3 started — HTTP 200
Top-level response keys: data, status
Data keys: browser_type, core_version, id, is_quick, port
Envelope http_code: 200

### Launcher / Start Quick Profile

ID: `46206122-33a08b11-7b3d-4957-b579-d1861fdffef8`

`POST https://launcher.mlx.yt:45001/api/v2/profile/quick`

**To be deprecated. Use Start Quick Profile v3 for starting quick browser profiles.**

Create a one-time quick browser profile, that opens up after the call is successfully made. Browsing activity and its related data is not saved after the profle has been stopped.

Fingerprint parameters need providing only if flags set to `Custom`.

Check out **Params** to see what each key-value pair is about. To copy the example request body, navigate to **Body**.

If you would like to avoid having your profiles updated to the latest available core, specify `auto_update_core` (`true` or `false`) and a specific `core_version`.  
Updating existing profiles to a specific core version is not supported.

**Mimic quick profiles will work with** **`custom_start_urls`** **only if** **`automation_type`** **is NOT specified. This is to be fixed soon. Stealthfox profiles work as expected.**

**NB: It is recommended to use the default values, which keep your browser cores up-to-date. Multilogin does not bear any responsability for ban or detection-related issues if profiles have a dated core version.**

**Required parameters:**

``` json
{
    "browser_type": "<string>",
    "os_type": "<string>",
    "parameters": {
        "flags": {
            "audio_masking": "value",
            "fonts_masking": "value",
            "geolocation_masking": "value",
            "geolocation_popup": "value",
            "graphics_masking": "value",
            "graphics_noise": "value",
            "localization_masking": "value",
            "media_devices_masking": "value",
            "navigator_masking": "value",
            "ports_masking": "value",
            "proxy_masking": "value",
            "screen_masking": "value",
            "timezone_masking": "value",
            "webrtc_masking": "value"
        }
        "fingerprint": {}
}

 ```

The number of parameters in `fingerprint` may vary depending on the flag values passed in the request body.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| browser_type | True | `Required`. Choose the browser type. Note: For `android` only mimic is supported! |
| auto_update_core | True | `Optional` You can skip specifying the value since your profiles will be updated to the latest core by default each time it is launched. |
| core_version | True | `Optional`.  You can skip specifying the value since your profiles will be updated to the latest core each time it is launched. |
| os_type | True | `Required`. Specify the OS. |
| automation | True | `Optional`. Specify the automation type. Mimic can work with any of the types. Stealthfox can only work with **selenium**. |
| is_headless | True | `Optional`. Enable headless mode. |
| proxy | True | `Optional` for `parameters`. Add a proxy to your profiles. |
| save_traffic | True | `Optional` for `proxy`. `false` is set by default. When set to `true`,  disables the loading of images/videos saving the proxy traffic. |
| parameters | True | `Required`. Specify parameters for your profiles. `flags`, `fingerprints`, `storage` **are required** for **parameters**. |
| flags | True | `Required`. Specify flags for your profiles. `webrtc_masking, proxy_masking, geolocation_popup, audio_masking, graphics_noise, ports_masking, navigator_masking, localization_masking, timezone_masking, graphics_masking, fonts_masking, media_devices_masking, screen_masking, geolocation_masking` **are required** for **parameters**. |
| webrtc_masking | True | `Required` for `flags`. |
| geolocation_popup | True | `Required` for `flags`. |
| audio_masking, graphics_noise | True | `Required` for `flags`. |
| proxy_masking | True | `Required` for `flags`. |
| navigator_masking, localization_masking, timezone_masking, graphics_masking, fonts_masking, media_devices_masking, screen_masking, ports_masking | True | `Required` for `flags`. |
| geolocation_masking | True | `Required` for `flags`. |
| canvas_noise | True | `Optional` for`flags`. The value is set based on the value of `graphics_noise` by default. To set a specific value for `canvas_noise`, include `canvas_noise` in your request body. |
| startup_behavior | True | `Optional` for `flags`. `recover` is set by default and allows opening profiles with the tabs from the last session. `custom` opens up profiles with provided custom pages in `custom_start_urls`. |
| fingerprint | True | `Required` for `parameters`. Specify fingerprints of your profiles if flags are set to `Custom`. |
| hardware_concurrency | True | `Required` for `navigator`. Specify the value for `hardware_concurrency` if the flag is `Custom`. |
| user_agent | True | `Required` for `navigator`. Specify the value for `user-agent`. |
| platform | True | `Required` for `navigator`. Specify the value for `platform` if the flag is `Custom`. |
| os_cpu | True | `Oprtional` for `navigator`. Specify the value for `os_cpu`if the flag is `Custom`. |
| accept_languages | True | `Required` for `localization`. Specify the value for `accept_languages` if the flag is `Custom`. |
| languages | True | `Required` for `localization`. Pass an empty string. |
| locale | True | `Required` for `localization`. Pass an empty string. |
| zone | True | `Required` for `timezone`.  Specify the value for `zone`. |
| vendor | True | `Required` for `graphic`. Specify the value for `vendor` if the flag is `Custom`. |
| renderer | True | `Required` for `graphic`. Specify the value for `renderer` if the flag is `Custom`. |
| vendor_id | True | `Optional` for `graphic`. Specify the value for `vendor_id` if the flag is `Custom`. |
| renderer_id | True | `Optional` for `graphic`. Specify the value for `renderer_id` if the flag is `Custom`. |
| public_ip | True | `Required` for `webrtc`. Specify the value for `public_ip` if the flag is `Custom`. |
| audio_outputs | True | `Required` for `media_devices`. Specify the value for `audio_outputs` if the flag is `Custom`. |
| video_inputs | True | `Required` for `media_devices`. Specify the value for `video_inputs` if the flag is `Custom`. |
| audio_inputs | True | `Required` for `media_devices`. Specify the value for `audio_inputs` if the flag is `Custom`. |
| width | True | `Required` for `screen`. Specify the value for `width` if the flag is `Custom`. |
| height | True | `Required` for `screen`.  Specify the value for `height` if the flag is `Custom`. |
| pixel_ratio | True | `Required` for `screen`. Specify the value for `pixel_ratio` if the flag is `Custom`. |
| ports | True | `Optional`. Specify the value for `ports` if the flag is `Custom`. |
| accuracy | True | `Required` for `geolocation`. Specify the value for `accuracy` if the flag is `Custom`. |
| altitude | True | `Required` for `geolocation`. Specify the value for `altitude` if the flag is `Custom`. |
| longitude | True | `Required` for `geolocation`. Specify the value for `longitude` if the flag is `Custom`. |
| latitude | True | `Required` for `geolocation`. Specify the value for `latitude` if the flag is `Custom`. |
| fonts | True | `Optional` for `fingerprints`. Specify the value for `fonts` if the flag is `Custom`. |
| cmd_params | True | `Optional` for `fingerprints`. Specify command line parameters for browsers. |
| custom_start_urls | True | `Optional`. Specify custom URLs. Max amount is 5. |
| max_touch_points | True | `Optional` for `fingerprint` with `android` os. Default is 5. |

**Body template** (`text`; chưa phải payload runnable):

```text
{
    "browser_type": "<string>",
    "os_type": "<string>",
    "automation": "<string>",
    "core_version": <integer>,
    "is_headless": <boolean>,
    "proxy": {
        "host": "<string>",
        "type": "<string>",
        "port": <integer>,
        "username": "<string>",
        "password": "<string>",
        "save_traffic": "<boolean>"
    },
    "parameters": {
        "flags": {
            "audio_masking": "<string>",
            "fonts_masking": "<string>",
            "geolocation_masking": "<string>",
            "geolocation_popup": "<string>",
            "graphics_masking": "<string>",
            "graphics_noise": "<string>",
            "localization_masking": "<string>",
            "media_devices_masking": "<string>",
            "navigator_masking": "<string>",
            "ports_masking": "<string>",
            "proxy_masking": "<string>",
            "screen_masking": "<string>",
            "timezone_masking": "<string>",
            "webrtc_masking": "<string>",
            "canvas_noise:": "<string>",
            "startup_behavior": "<string>"
        },
        "fingerprint": {
            "navigator": {
                "hardware_concurrency": <integer>,
                "platform": "<string>",
                "user_agent": "<string>",
                "os_cpu": "<string>"
            },
            "localization": {
                "languages": "<string>",
                "locale": "<string>",
                "accept_languages": "<string>"
            },
            "timezone": {
                "zone": "<string>"
            },
            "graphic": {
                "renderer": "<string>",
                "vendor": "<string>"
            },
            "webrtc": {
                "public_ip": "<string>"
            },
            "media_devices": {
                "audio_inputs": <integer>,
                "audio_outputs": <integer>,
                "video_inputs": <integer>
            },
            "screen": {
                "height": <integer>,
                "pixel_ratio": <double>,
                "width": <integer>
            },
            "geolocation": {
                "accuracy": <number>,
                "altitude": <number>,
                "latitude": <number>,
                "longitude": <number>
            },
            "ports": [
                <integer>,
            ],
            "fonts": [
                "<string>"
            ],
            "cmd_params": {
                "params": [
                    {
                        "flag": "<string>",
                        "value": "<boolean>"
                    }
                ]
            }
        },
        "custom_start_urls": [
            "<string>"
        ]
    }
}
```

Saved example: Quick Profile Started — HTTP 200
Top-level response keys: data, status
Data keys: browser_type, core_version, id, is_quick, port
Envelope http_code: 200

### Launcher / Stop Browser Profile

ID: `46206122-2a80faba-b99c-402f-918b-9adf2ccf8859`

`GET https://launcher.mlx.yt:45001/api/v1/profile/stop/p/:profile_id`

Stop a browser profile.

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | False | `Required`. Specify the ID of the profile to launch. |

Saved example: Profile Removed — HTTP 200
Top-level response keys: status
Envelope http_code: 200

### Launcher / Stop All Profiles

ID: `46206122-dba97c75-3505-4fbc-9b4f-ca3628d59a7c`

`GET https://launcher.mlx.yt:45001/api/v1/profile/stop_all?type=all, regular, quick`

Stop all the launched profiles.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| type | False | `Optional`. Specify the type of profile to stop. `all` is set by default. |

Saved example: Profiles Stopped — HTTP 200
Top-level response keys: status
Envelope http_code: 200

### Launcher / Get Version

ID: `46206122-c172af78-35ad-40dd-952d-9fccf4505afa`

`GET https://launcher.mlx.yt:45001/api/v1/version`

Fetch the launcher version.

**Body template** (`json`; chưa phải payload runnable):

```text

```

Saved example: Version Fetched — HTTP 200
Top-level response keys: data, status
Data keys: env, version
Envelope http_code: 200

### Launcher / Get Profile Status

ID: `46206122-b592e987-5015-434e-ad92-82d44f654bb6`

`GET https://launcher.mlx.yt:45001/api/v1/profile/status/p/:profile_id`

Get the status of a single profile launched during the last session with Agent. If Agent is restarted, there will be no data to fetch.

Possible profile statuses:

- `download_browser_profile_metadata`
    
- `download_browser_profile_data`
    
- `download_browser_core`
    
- `download_finished`
    
- `download_meta_error`
    
- `download_data_error`
    
- `download_core_error`
    
- `download_meta_finished`
    
- `download_data_finished`
    
- `download_core_finished`
    
- `validate_proxy`
    
- `validate_proxy_error`
    
- `start_browser`
    
- `start_browser_error`
    
- `browser_running`
    
- `stopped`

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | False | `Required`. Specify the ID of the profile to launch. |

Saved example: Status Fetched — HTTP 200
Top-level response keys: data, status
Data keys: browser_type, core_version, folder_id, in_use_by, is_quick, last_launched_at, last_launched_by, last_launched_on, message, name, profile_id, status, timestamp, workspace_id
Envelope http_code: 200

### Launcher / Get All Profiles Status

ID: `46206122-7b023e16-0961-4f15-b3c2-7b728f9bec98`

`GET https://launcher.mlx.yt:45001/api/v1/profile/statuses`

Get the status of all the profiles launched during the last session with Agent. If Agent is restarted, there will be no data to fetch.

**Possible profile statuses:**

- `download_browser_profile_metadata`
    
- `download_browser_profile_data`
    
- `download_browser_core`
    
- `download_finished`
    
- `download_meta_error`
    
- `download_data_error`
    
- `download_core_error`
    
- `download_meta_finished`
    
- `download_data_finished`
    
- `download_core_finished`
    
- `validate_proxy`
    
- `validate_proxy_error`
    
- `start_browser`
    
- `start_browser_error`
    
- `browser_running`
    
- `stopped`
    

**Possible script statuses:**

- `running`
    
- `finished`
    
- `stopped`
    
- `error`

Saved example: Status Fetched — HTTP 200
Top-level response keys: data, status
Data keys: active_counter, states
Envelope http_code: 200

### Launcher / Get All Quick Profiles Status

ID: `46206122-e16d542a-43c3-4d37-bbe5-c699e7b5d9d0`

`GET https://launcher.mlx.yt:45001/api/v1/profile/quick/statuses`

Get the status of all the quick profiles launched during the last session with Agent. If Agent is restarted, there will be no data to fetch.

**Possible profile statuses:**

- `download_browser_profile_metadata`
    
- `download_browser_profile_data`
    
- `download_browser_core`
    
- `download_finished`
    
- `download_meta_error`
    
- `download_data_error`
    
- `download_core_error`
    
- `download_meta_finished`
    
- `download_data_finished`
    
- `download_core_finished`
    
- `validate_proxy`
    
- `validate_proxy_error`
    
- `start_browser`
    
- `start_browser_error`
    
- `browser_running`
    
- `stopped`

Saved example: Status Fetched — HTTP 200
Top-level response keys: data, status
Data keys: active_counter, states
Envelope http_code: 200

### Launcher / Loaded Browser Cores

ID: `46206122-08c3a286-977a-48c3-a88f-67284cb00c3b`

`GET https://launcher.mlx.yt:45001/api/v1/loaded_browser_cores`

Fetch a list of cores saved on your machine.

Saved example: Cores Loaded — HTTP 200
Top-level response keys: data, status
Envelope http_code: 200

### Launcher / Browser Core List

ID: `46206122-db0a1c1f-0973-4826-9951-724787b6965f`

`GET https://api.multilogin.com/bcs/core/list`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Fetch a list of available browser core versions for a given browser.

**NB: Make certain that Launcher is running before calling the endpoint.**

**Required parameters for Strict mode:**

``` json
{
  "browser_type": ""
}

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| browser_type | True | Specify the browser type. Defaults to `mimic`. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "browser_type": "<string>"
}
```

Saved example: Browser Core List Fetched — HTTP 200
Top-level response keys: status, data
Data keys: core_versions
Envelope http_code: 200

### Launcher / Load Browser Core

ID: `46206122-922e36c8-0b79-480b-b17c-dec5694563ad`

`GET https://launcher.mlx.yt:45001/api/v1/load_browser_core?browser_type=mimic,stealthfox&version=123`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Load a particular browser core from the server.

Please note that launching profiles with a dated core version may significantly increase the chances of getting detected.

**Required parameters for Strict mode:**

``` json
"browser_type": "value>",
"version" : <number>

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| browser_type | False | `Required`. Specify the browser type. Defaults to `mimic` |
| version | False | `Required`. Specify the core version. Defaults to `latest`. |

Saved example: Core Loaded — HTTP 500
Top-level response keys: status
Envelope http_code: 200

### Launcher / Delete Browser Core

ID: `46206122-0fb79d90-1b60-4329-9c60-fe5c5ccf4e19`

`DELETE https://launcher.mlx.yt:45001/api/v1/delete_browser_core?browser_type=mimic,stealthfox&version=116`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Delete a browser core from your machine.

**Required parameters for Strict mode:**

``` json
"browser_type": "value>",
"version" : <number>

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| browser_type | False | `Required`. Specify the browser type. Defaults to `mimic` |
| version | False | `Required`. Specify the core version. Defaults to `latest`. |

Saved example: Core Deleted — HTTP 200
Top-level response keys: status
Envelope http_code: 200

### Launcher / Validate Proxy

ID: `46206122-fa8703a8-5d02-4628-8116-36ee4bd963c1`

`POST https://launcher.mlx.yt:45001/api/v1/proxy/validate`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Check your proxy connection.

**Required parameters for Strict mode:**

``` json
{
  "type": "<string>",
  "host": "<string>",
  "port": <number>,
  "username": "<string>",
  "password": "<string>"
}

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| type | True | `Required`. Specify the proxy type. Defaults to `http`. |
| host | True | `Required`. Specify the proxy host. |
| port | True | `Required`. Specify the proxy port. |
| username | True | `Required`. Specify the proxy username. |
| password | True | `Required`. Specify the proxy password. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "type": "<string>",
  "host": "<string>",
  "port": <interger>,
  "username": "<string>",
  "password": "<string>"
}
```

Saved example: Validate Proxy — HTTP 200
Top-level response keys: data, status
Data keys: accuracy, altitude, country_code, ip, latitude, longitude, timezone
Envelope http_code: 200

### Launcher / Cookie Import

ID: `46206122-9a88934f-f1ac-43e7-a415-e958df83f648`

`POST https://launcher.mlx.yt:45001/api/v1/cookie_import`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Import cookies or pre-made cookies into your profiles.

Check out **Params** to see what each key-value pair is about. To copy the example request body, please navigate to **Body**.

If the endpoint is beind called programmatically, a text file with a JSON object will be taken as payload.

For Postman users, provide cookies as a JSON object converted to a string directly in to `cookies`.

**Required parameters for Strict mode:**

``` json
{
  "profile_id": "<string>",
  "import_advanced_cookies": <boolean>,
  "cookies" : "[{\"secure\":true,\"session\":false,\"hostOnly\":false,\"name\":\"compass_uid\",\"path\":\"/\",\"value\":\"7a44a512-551e-4b2b-847d-4ad9df82a74e\",\"domain\":\".eluniversal.com.mx\",\"storeId\":\"0\",\"httpOnly\":false,\"expirationDate\":1729843683463}]"
}

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | True | `Required` |
| folder_id | True | `Required`. Defaults to `default profile ID` |
| import_advanced_cookies | True | `Required`. Set `true` if you want to imported the created cookies. |
| cookies | True | `Optional`. Only add this if you are using `import_advanced_cookies` to `false` |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "profile_id": "<string>",
  "folder_id": "<string>",
  "import_advanced_cookies": <boolean>,
  "cookies" : "[{\"secure\":true,\"session\":false,\"hostOnly\":false,\"name\":\"compass_uid\",\"path\":\"/\",\"value\":\"7a44a512-551e-4b2b-847d-4ad9df82a74e\",\"domain\":\".eluniversal.com.mx\",\"storeId\":\"0\",\"httpOnly\":false,\"expirationDate\":1729843683463}]"
}
```

Saved example: Cookie Import — HTTP 200
Top-level response keys: status
Envelope http_code: 200

### Launcher / Cookie Export

ID: `46206122-618fb3e0-56e7-4e06-9b0f-04c774953c2a`

`POST https://launcher.mlx.yt:45001/api/v1/cookie_export`

Export cookies from your browser profiles.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | True | `Required` |
| folder_id | True | `Required` |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "profile_id": "<string>",
  "folder_id": "<string>"
}
```

Saved example: Cookie Import — HTTP 200
Top-level response keys: data, status
Data keys: cookies, profile_id, timestamp
Envelope http_code: 200

### Launcher / Convert QBP to Profile

ID: `46206122-359f06d1-5d8a-45bc-857f-8e9d874d63a7`

`POST https://launcher.mlx.yt:45001/api/v1/profile/quick/save`

In order to use the Convert from QBP to normal profile, you must have the QBP up and running.

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "data": [
    {
      "profile_id": "QBP_id"
    }
  ]
}
```

Saved example: Convert QBP to Profile — HTTP 200
Top-level response keys: status
Envelope http_code: 200

### Launcher / Get QBP status

ID: `46206122-bf788506-7461-4582-86e2-a7cfb58d1392`

`GET https://launcher.mlx.yt:45001/api/v1/profile/quick/statuses`

This endpoint makes an HTTP GET request to retrieve the quick statuses of profiles. The request does not require a request body as it is a GET request. The response will include the status information for the profiles, including details such as profile ID, status message, and timestamp.

**Body template** (`json`; chưa phải payload runnable):

```text

```

Saved example: Convert QBP to Profile — HTTP 200
Top-level response keys: data, status
Data keys: active_counter, states
Envelope http_code: 200

### Profile Access Management / User Sign In

ID: `46206122-fd4763f8-350f-416e-a2d4-ac13f75c5ca2`

`POST https://api.multilogin.com/user/signin`

Log in to your account. The password must be hashed with the md5 algorithm.

Check out **Params** to see what each key-value pair is about.

To copy the example request body, please navigate to **Body**.

The token has 30 minutes of lifetime. Upon expiration, you may refresh it with `POST /user/refresh_token` to obtain a new one.

To have higher rate limits and a longer token lifetime, it is recommended to get the [automation token](https://documenter.getpostman.com/view/28533318/2s946h9Cv9#918a9c42-cb0f-497f-9bdd-a44d9d760be5).

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| email | True | `Required`. Enter your account email. |
| password | True | `Required`. Enter your account password. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "email": "<string>",
  "password": "<string>"
}
```

Saved example: Signed In — HTTP 500
Top-level response keys: status, data
Data keys: refresh_token, token
Envelope http_code: 200

### Profile Access Management / User Refresh Token (Switch Workspace)

ID: `46206122-5da68f7f-ca3c-4a5f-97d8-4170c167ddb2`

`POST https://api.multilogin.com/user/refresh_token`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Refresh the JWT token. The endpoint allows retrieving a new token if the current one has expired or switching to another workspace.

The endpoint is also used to switch to a given workspace. To get the workspace ID to switch to, refer to `GET /user/workspaces`.

Check out **Params** to see what each key-value pair is about. To copy the example request body, please navigate to **Body.**

**Required parameters for Strict mode:**

``` json
{
  "email": "<string>",
  "refresh_token": "<string>",
  "workspace_id": "<string>"
}

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| email | True | `Required`. Enter your account email. |
| refresh_token | True | `Required`. Enter your refresh token. Can be fetched with `POST user/signin`. |
| workspace_id | True | `Required`. Specify the workspace, in which you would like to work or switch to. Can be fetched with `GET /user/workspaces`. Defaults to `current sign-in workspace`. |
|  | True |  |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "email": "<string>",
  "refresh_token": "<string>",
  "workspace_id": "<string>"
}
```

Saved example: Token Refreshed — HTTP 500
Top-level response keys: status, data
Data keys: refresh_token, token
Envelope http_code: 200

### Profile Access Management / User Revoke Token

ID: `46206122-05b8e164-0907-4ca2-8908-ec8596c6cad7`

`POST {{baseUrl}}/user/revoke_tokens`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Revoke user's active tokens.

Calling the endpoint without passing any payload will revoke all the current tokens (both automation and regulaar token).

If you want to revoke a parcticular type of the token, specify it in the `"is_automation"` object.

**Required parameters for Strict mode:**

``` json
"token": "<string>",
"is_automation": <boolean>

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| token | True | `Optional`. Specify the token to revoke. Defaults to `current token`. |
| is_automation | True | `Optional`. Specify the token type to revoke. Defaults to `false`. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "token": "<string>",
  "is_automation": <boolean>
}
```

Saved example: Token Revoked — HTTP 500
Top-level response keys: status
Envelope http_code: 200

### Profile Access Management / User Change Password

ID: `46206122-3ea2166c-fe98-4b01-9134-116cb8f2ef3a`

`POST https://api.multilogin.com/user/change_password`

Change your password. The new password must also be md5-hashed.

After the password has been changed, the current token will be revoked. To carry on, you need to log in again.

Check out **Params** to see what each key-value pair is about. To copy the example request body, please navigate to **Body**.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| new_password | True | `Required`. Enter your new password. |
| password | True | `Required`. Enter your current password. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "new_password": "<string>",
  "password": "<string>"
}
```

Saved example: Password Changed — HTTP 500
Top-level response keys: status, data
Envelope http_code: 200

### Profile Access Management / User Workspaces

ID: `46206122-caf854a8-8717-42ba-943f-ce79f8996051`

`GET https://api.multilogin.com/user/workspaces`

Get a list of workspaces. There may be multiple workspaces if you have been invited to join other users' workspaces.

To switch to a workspace, to which you have been invited, select the workspace ID and pass to **POST /user/refresh_token** as the value of `workspace_id`.

Saved example: Workspace Information Fetched — HTTP 200
Top-level response keys: status, data
Data keys: total_count, workspaces
Envelope http_code: 200

### Profile Access Management / User Token List

ID: `46206122-25e34ae7-1a65-412d-9ff0-7b6e88c37bcd`

`GET https://api.multilogin.com/user/tokens_list`

Fetch all the active tokens for a specific account.

Saved example: List Fetched — HTTP 200
Top-level response keys: data, status
Data keys: tokens
Envelope http_code: 200

### Profile Access Management / Workspace Restrictions

ID: `46206122-56d96ba1-f0b1-46b6-a19d-f2a99c385934`

`GET {{baseUrl}}/workspace/restrictions`

Fetch the workspace details, which is currently in use. Workspace restrictions provide information on automation feature availability, allowed browser types, the number of available team members, the profile count and other valuable workspace data.

Saved example: Restrictions Fetched — HTTP 200
Top-level response keys: status, data
Data keys: allowed_browser_types, automation_available, cloud_profiles_count, expires_at, folders_count, local_profiles_count, plan_name, ratelimit, team_members_count
Envelope http_code: 200

### Profile Access Management / Workspace Folders

ID: `46206122-fe88e7d3-3c1d-4e76-8e4d-d6b9a1dd3002`

`GET https://api.multilogin.com/workspace/folders`

Get a list of available folders by workspace. Workspace_id will be taken from the token passed in the headers. If you need to switch workspaces, select the required workspace ID and call to refresh the token.

Saved example: Workspace Folders Fetched — HTTP 500
Top-level response keys: status, data
Data keys: folders
Envelope http_code: 200

### Profile Access Management / Workspace Folders For User

ID: `46206122-cc53f0ee-7da3-4915-9c41-8cc725b6d76b`

`GET {{baseUrl}}/workspace/folders_for_user?email=foo@bar.com`

Get a list of available folders by workspace ID and user email.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| email | False | `Required`. Specify the user's email. |

Saved example: User Folders Fetched — HTTP 500
Top-level response keys: status, data
Data keys: folders
Envelope http_code: 200

### Profile Access Management / Workspace Statistics

ID: `46206122-1800515f-c738-4f30-a4ef-de299bc0ae2b`

`GET https://api.multilogin.com/workspace/statistics`

Get statistics for the selected workspace.

Saved example: Workspace Statistics Fetched — HTTP 200
Top-level response keys: status, data
Data keys: profiles_cloud_count, profiles_cloud_limit, profiles_local_count, profiles_local_limit, users_count, users_limit
Envelope http_code: 200

### Profile Access Management / Workspace Automation Token

ID: `46206122-66713766-8eca-41a6-b259-c4a58364aef5`

`GET https://api.multilogin.com/workspace/automation_token?expiration_period=1h,3h,5h,16h,24h,48h,1w,2w,3w,1mo,no_exp`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Get automation token. Available for users who have a subscription plan with automation enabled. The token has a longer expiration period and higher rate limits.

To use the token, make certain that your account has automation enabled and retrieve the token once by calling the endpoint to save and pass it to all the endpoints to call.

For more information, visit [the support page](https://help.multilogin.com/api/automation-token) specifically dedicated to explain in detail how to work with automation tokens.

**Required parameters for Strict mode:**

``` json
"expiration_period":"<string>"

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| expiration_period | False | `Required`. Specify the token lifetime. Defaults to `24h`. |

Saved example: Automation Token Fetched — HTTP 200
Top-level response keys: status, data
Data keys: token
Envelope http_code: 200

### Profile Access Management / Workspace Create Folder

ID: `46206122-5751069f-655a-4346-ad69-ca16ae417cdb`

`POST {{baseUrl}}/workspace/folder_create`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Create a new folder in the current workspace.

Check out **Params** to see what each key-value pair is about. To copy the example request body, please navigate to **Body.**

**Required parameters for Strict mode:**

``` json
"name": "<string>",
"comment":"<string>"

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| name | True | `Required`. Name your folder. Defaults to `"New Folder"`. |
| comment | True | `Optional`. Add comments if necessary. Defaults to empty string `""`. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "name": "<string>",
  "comment": "<string>"
}
```

Saved example: Folder Created — HTTP 500
Top-level response keys: status, data
Data keys: id
Envelope http_code: 201

### Profile Access Management / Workspace Update Folder

ID: `46206122-52b99be7-eb38-4e57-82cb-6aac25a4fe4d`

`POST {{baseUrl}}/workspace/folder_update`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Update the folder.

**Required parameters for Strict mode:**

``` json
"name": "<string>",
"comment":"<string>",
"folder_id":"<string>"

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| folder_id | True | `Required`. Specify the folder ID. |
| name | True | `Required`. Specify the new folder name. |
| comment | True | `Optional`. Add comments if necessary. Defaults to empty string `""`. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "folder_id": "<string>",
  "name": "<string>",
  "comment": "<string>"
}
```

Saved example: Folder Changed — HTTP 500
Top-level response keys: status, data
Envelope http_code: 200

### Profile Access Management / Workspace Remove Folders

ID: `46206122-4107b626-696b-4339-8706-6815c5c2399a`

`POST {{baseUrl}}/workspace/folders_remove`

Remove folders in the current workspace.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. Specify the folder ID to remove, |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "ids": [
    "<string>"
  ]
}
```

Saved example: Folder Removed — HTTP 500
Top-level response keys: status, data
Envelope http_code: 200

### Profile Access Management / Workspace Leave

ID: `46206122-647449c7-936c-4d35-8d95-51115323e699`

`POST https://api.multilogin.com/workspace/leave`

Leave the selected workspace.

Check out **Params** to see what each key-value pair is about. To copy the example request body, please navigate to **Body.**

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| workspace_id | True | `Required`. Specify the workspace, which you would like to leave. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "workspace_id": "<string>"
}
```

Saved example: Workspace Left — HTTP 500
Top-level response keys: status, data
Envelope http_code: 200

### Profile Management / Profile Create

ID: `46206122-8adac9ee-5307-4b33-8c4f-1e064105ac06`

`POST https://api.multilogin.com/profile/create`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Create a new regular profile. Fingerprint parameters need providing only if flags set to `Custom`.

Check out **Params** to see what each key-value pair is about. To copy the example request body, navigate to **Body**.

If you would like to avoid having your profiles updated to the latest available core, specify `auto_update_core` (`true` or `false`) and a specific `core_version`.

**NB: It is recommended to use the default values, which keep your browser cores up-to-date. Multilogin does not bear any responsability for ban or detection-related issues if profiles have a dated core version.**

**Required parameters for Strict mode:**

``` json
{
    "name": "<string>",
    "browser_type": "<string>",
    "folder_id": "<string>",
    "os_type": "<string>",
    "auto_update_core": <boolean>,
    "core_version": <number>,
    "parameters": {
        "flags": {
            "audio_masking": "value",
            "fonts_masking": "value",
            "geolocation_masking": "value",
            "geolocation_popup": "value",
            "graphics_masking": "value",
            "graphics_noise": "value",
            "localization_masking": "value",
            "media_devices_masking": "value",
            "navigator_masking": "value",
            "ports_masking": "value",
            "proxy_masking": "value",
            "screen_masking": "value",
            "timezone_masking": "value",
            "webrtc_masking": "value",
            "canvas_noise": "value",
            "startup_behavior": "value"
        },
        "storage": {
            "is_local": <boolean>,
            "save_service_worker": <boolean>
        },
        "times": <number>,
        "notes": "<string>",
        "custom_start_urls": [
         "string"
          ],
        "fingerprint": {
          "cmd_params": {
           "params": [
          {
            "flag": "string",
            "value": "string"
          }
          ]
         },
         }
}

 ```

The number of parameters in `fingerprint` may vary depending on the flag values passed in the request body.<p><strong>ISP proxies:</strong> to attach an MLX-managed ISP proxy, set <code>parameters.proxy.isp_ip_id</code> to the full proxy id returned by <strong>List ISP Proxies</strong> (Proxy folder) and send <code>"host": ""</code> alongside it - the <code>host</code> key must be present, but its value is ignored: connection details and credentials are resolved server-side from the registry when the profile starts. <code>type</code> / <code>port</code> / <code>username</code> / <code>password</code> can be omitted; a supplied <code>type</code> is ignored - the protocol comes from the registry.</p><p>Minimal proxy object:</p><pre><code>"proxy": { "host": "", "isp_ip_id": "&lt;uuid&gt;" }</code></pre><p>Restrictions: an ISP proxy is single-use - <code>times</code> must be <code>1</code> (other values return <code>400</code>), and attaching an IP already assigned to another profile returns <code>409</code>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| name | True | `Required`. Name your profiles.  |
| browser_type | True | `Required`. Choose the browser type. Note: For `android` only mimic is supported! Defaults to `mimic`. |
| folder_id | True | `Required`. Specify the folder in which profiles will be created. The ID can be retrived with `GET /workspace/folders.` |
| os_type | True | `Required`. Specify the OS. Defaults to `windows`. |
| core_version | True | `Optional`. You can skip specifying the value since your profiles will be updated to the latest core by default each time it is launched. Cannot specify the version that is 6 versions older then the current latest one. |
| core_minor_version | True | `Optional`. Specify the minor version based on its availability. |
| auto_update_core | True | `Optional` You can skip specifying the value since your profiles will be updated to the latest core by default each time it is launched. Defaults to `true`. |
| tags | True | `Optional`. Specify tags. Max number is 10. |
| times | True | `Optional`. Specify a number of profiles to create. Defaults to `1`. |
| notes | True | `Optional`. Add notes to your profiles. Defaults to an empty string`""`. Max length 400 is chars. |
| parameters | True | `Required`. Specify parameters for your profiles. `flags`, `fingerprint`, `storage` **are required** for **parameters**. |
| flags | True | `Required`. Specify flags for your profiles. `webrtc_masking, proxy_masking, geolocation_popup, audio_masking, graphics_noise, ports_masking, navigator_masking, localization_masking, timezone_masking, graphics_masking, fonts_masking, media_devices_masking, screen_masking, geolocation_masking` **are required** for **parameters**. |
| webrtc_masking | True | `Required` for `flags`. Defaults to `mask`. |
| audio_masking, graphics_noise, ports_masking | True | `Required` for `flags`. Defaults to `natural` for audio_masking and `mask` for rest. |
| proxy_masking | True | `Required` for `flags`. Defaults to `disabled` unless proxy is configured, than defaults to `custom`. |
| geolocation_popup | True | `Required` for `flags`. Defaults to `prompt`. |
| navigator_masking, localization_masking, timezone_masking, graphics_masking, fonts_masking, media_devices_masking, screen_masking | True | `Required` for `flags`. Defaults to `mask` and for media_devices_masking defaults to `natural`. |
| geolocation_masking | True | `Required` for `flags`. Defaults to `mask`. |
| quic_mode | True | `Optional` for `flags`. `disabled` by default. |
| startup_behavior | True | `Optional` for `flags`. `recover` is set by default and allows opening profiles with the tabs from the last session. `custom` opens up profiles with provided custom pages in `custom_start_urls`. Defaults to `recover`. |
| canvas_noise | True | `Optional` for `flags`. The value is set based on the value of `graphics_noise` by default. To set a specific value for `canvas_noise`, include `canvas_noise` in your request body. |
| fingerprint | True | In Strict mode is`Required` for `parameters`. Specify fingerprints of your profiles if flags are set to `Custom`. Defaults to `optional` unless custom is set. |
| hardware_concurrency | True | `Required` for `navigator`. Specify the value for `hardware_concurrency` if the flag is `Custom`. |
| user_agent | True | `Required` for `navigator`. Specify the value for `user-agent`. |
| platform | True | `Required` for `navigator`. Specify the value for `platform` if the flag is `Custom`. |
| os_cpu | True | `Optional` for `navigator`. Specify the value for `os_cpu`if the flag is `Custom`. |
| accept_languages | True | `Required` for `localization`. Specify the value for `accept_languages` if the flag is `Custom`. |
| languages | True | `Required` for `localization`. |
| locale | True | `Required` for `localization`. |
| zone | True | `Required` for `timezone` Specify the value for `zone`. |
| vendor | True | `Required` for `graphic`. Specify the value for `vendor` if the flag is `Custom`. |
| renderer | True | `Required` for `graphic`. Specify the value for `renderer` if the flag is `Custom`. |
| vendor_id | True | `Optional` for `graphic`. Specify the value for `vendor_id` if the flag is `Custom`. |
| renderer_id | True | `Optional` for `graphic`. Specify the value for `renderer` if the flag is `Custom`. |
| public_ip | True | `Required` for `webrtc`. Specify the value for `renderer_id` if the flag is `Custom`. |
| audio_outputs | True | `Required` for `media_devices`. Specify the value for `audio_outputs` if the flag is `Custom`. |
| audio_inputs | True | `Required` for `media_devices`. Specify the value for `audio_inputs` if the flag is `Custom`. |
| video_inputs | True | `Required` for `media_devices`. Specify the value for `video_inputs` if the flag is `Custom`. |
| width | True | `Required` for `screen`. Specify the value for `width` if the flag is `Custom`. The Screen Resolution endpoint is found under Profile Management->[Screen Resolution](https://documenter.getpostman.com/view/28533318/2s946h9Cv9#5a8d793b-3cd0-4ae3-a3f6-caa9143315c2) |
| height | True | `Required` for `screen`. Specify the value for `height` if the flag is `Custom`. The Screen Resolution endpoint is found under Profile Management->[Screen Resolution](https://documenter.getpostman.com/view/28533318/2s946h9Cv9#5a8d793b-3cd0-4ae3-a3f6-caa9143315c2) |
| pixel_ratio | True | `Required` for `screen`. Specify the value for `pixel_ratio` if the flag is `Custom`. |
| accuracy | True | `Required` for `geolocation`. Specify the value for `accuracy` if the flag is `Custom`. |
| altitude | True | `Required` for `geolocation`. Specify the value for `altitude` if the flag is `Custom`. |
| latitude | True | `Required` for `geolocation`. Specify the value for `latitude` if the flag is `Custom`. |
| longitude | True | `Required` for `geolocation`. Specify the value for `longitude` if the flag is `Custom`. |
| ports | True | `Optional` for `fingerprint`. Specify the value for `ports` if the flag is `Custom`. |
| fonts | True | `Optional` for `fingerprint`. Specify the value for `fonts` if the flag is `Custom`. |
| cmd_params | True | `Optional` for `fingerprint`. Specify command line parameters for browsers. Defaults to an empty string `""`. |
| is_local | True | `Required` for `storage`. Defaults to `true`. |
| save_service_worker | True | `Optional` for `storage`. Defaults to `true`. |
| proxy | True | `Optional` for `fingerprint`. Add a proxy to your profiles. |
| parameters.proxy.isp_ip_id | True | `Optional`. MLX-managed ISP proxy id - get it from `List ISP Proxies` in the Proxy folder. Send `"host": ""` alongside it (the key is required, the value is ignored); `type` / `port` / `username` / `password` can be omitted - connection details are resolved server-side. In this endpoint the proxy object lives under `parameters`. |
| save_traffic | True | `Optional` for `proxy`. `false` is set by default. When set to `true`,  disables the loading of images/videos saving the proxy traffic. |
| custom_start_urls | True | `Optional` for `fingerprint`. Specify custom URLs. Max amount is 5. Defaults to `optional` unless custom is set. |
| max_touch_points | True | `Optional` for `fingerprint` with `android` os. Default is 5. |

**Body template** (`text`; chưa phải payload runnable):

```text
{
    "name": "<string>",
    "browser_type": "<string>",
    "folder_id": "<string>",
    "os_type": "<string>",
    "core_version": <integer>,
    "core_minor_version": <integer>,
    "times": <integer>,
    "notes": "<string>",
    "parameters": {
        "flags": {
            "audio_masking": "<string>",
            "fonts_masking": "<string>",
            "geolocation_masking": "<string>",
            "geolocation_popup": "<string>",
            "graphics_masking": "<string>",
            "graphics_noise": "<string>",
            "localization_masking": "<string>",
            "media_devices_masking": "<string>",
            "navigator_masking": "<string>",
            "ports_masking": "<string>",
            "proxy_masking": "<string>",
            "screen_masking": "<string>",
            "quic_mode": "<string>",
            "timezone_masking": "<string>",
            "webrtc_masking": "<string>",
            "canvas_noise:": "<string>",
            "startup_behavior": "<string>"
        },
        "storage": {
            "is_local": <boolean>,
            "save_service_worker": <boolean>
        },
        "fingerprint": {
            "navigator": {
                "hardware_concurrency": <integer>,
                "platform": "<string>",
                "user_agent": "<string>",
                "os_cpu": "<string>"
            },
            "localization": {
                "languages": "<string>",
                "locale": "<string>",
                "accept_languages": "<string>"
            },
            "timezone": {
                "zone": "<string>"
            },
            "graphic": {
                "renderer": "<string>",
                "vendor": "<string>"
            },
            "webrtc": {
                "public_ip": "<string>"
            },
            "media_devices": {
                "audio_inputs": <integer>,
                "audio_outputs": <integer>,
                "video_inputs": <integer>
            },
            "screen": {
                "height": <integer>,
                "pixel_ratio": <double>,
                "width": <integer>
            },
            "geolocation": {
                "accuracy": <number>,
                "altitude": <number>,
                "latitude": <number>,
                "longitude": <number>
            },
            "ports": [
                <integer>,
            ],
            "fonts": [
                "<string>"
            ],
            "cmd_params": {
                "params": [
                    {
                        "flag": "<string>",
                        "value": "<boolean>"
                    }
                ]
            }
        },
        "proxy": {
            "host": "<string>",
            "type": "<string>",
            "port": <integer>,
            "username": "<string>",
            "password": "<string>",
            "save_traffic": "<boolean>",
            "isp_ip_id": "<string>"
        },
        "custom_start_urls": [
            "<string>"
        ]
    }
}
```

Saved example: Profile Created — HTTP 201
Top-level response keys: status, data
Data keys: ids
Envelope http_code: 201

### Profile Management / Profile Search

ID: `46206122-107a7200-9770-40bc-b292-fc7f5d715d3b`

`POST https://api.multilogin.com/profile/search`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Search profiles.

**Required parameters for Strict mode:**

``` json
{
  "is_removed": <boolean>,
  "core_version": <integer>,
  "limit": <integer>,
  "offset": <integer>,
  "search_text": "<string>",
  "folder_id": "<string>",
  "storage_type": "<string>",
  "order_by": "<string>",
  "sort": "<string>"
}
// The request body with full parameters
// {
//     "is_removed": <boolean>,
//     "core_version": <integer>,
//     "limit": <integer>,
//     "offset": <integer>,
//     "search_text": "<string>",
//     "folder_id": "<string>",
//     "storage_type": "<string>",
//     "order_by": "<string>",
//     "created_from": "<string>",
//     "created_to": "<string>",
//     "updated_from": "<string>",
//     "updated_to": "<string>",
//     "last_launched_from": "<string>",
//     "last_launched_to": "<string>",
//     "last_launched_by": "<string>",
//     "last_launched_on": "<string>",
//     "last_updated_by": "<string>",
//     "in_use_by": "<string>",
//     "created_by": "<string>",
//     "sort": "<string>"
// }

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| is_removed | True | `Required`. Specify which type of profiles to search from. Defaults to `false`. |
| limit | True | `Required`. Specify the number of profiles to search. Defaults to `10`. |
| offset | True | `Required`. Specify the number of profiles to skip from the beginning of the returned data before displaying the results. 0 means starting from the beginning. Defaults to `0`. |
| search_text | True | `Required`. Search profiles by name. `maxLength`: 50 characters. An empty string searches from all the profiles. |
| storage_type | True | `Required`. Specify the storage type of profiles to search. |
| folder_id | True | `Optional`. Specify the folder in which searching is done |
| order_by | True | `Optional`. Order to sort resulting list of profiles. |
| sort | True | `Optional`.  Specify the order order of sorting. Defaults to `asc`. |
| core_version | True | `Optional`. Specify the core version. |
| created_from | True | `Optional`. Specify the start of the date range. |
| created_to | True | `Optional`. Specify the end of the date range. |
| updated_from | True | `Optional`.  Specify the start of the date range. |
| updated_to | True | `Optional`. Specify the end of the date range. |
| last_launched_from | True | `Optional`. Specify the start of the date range. |
| last_launched_to | True | `Optional`. Specify the end of the date range. |
| last_launched_by | True | `Optional`. Specify the email. |
| last_launched_on | True | `Optional`. Specify machine_id. |
| last_updated_by | True | `Optional`. Specify the email. |
| in_use_by | True | `Optional`. Specify the email. |
| created_by | True | `Optional`. Specify the email. |
| tags | True | `Optional`. Specify the tags. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "is_removed": <boolean>,
  "core_version": <integer>,
  "limit": <integer>,
  "offset": <integer>,
  "search_text": "<string>",
  "folder_id": "<string>",
  "storage_type": "all",
  "order_by": "created_at",
  "sort": "asc"
}

// The request body with full parameters
// {
//     "is_removed": <boolean>,
//     "core_version": <integer>,
//     "limit": <integer>,
//     "offset": <integer>,
//     "search_text": "<string>",
//     "folder_id": "<string>",
//     "storage_type": "<string>",
//     "order_by": "<string>",
//     "created_from": "<string>",
//     "created_to": "<string>",
//     "updated_from": "<string>",
//     "updated_to": "<string>",
//     "last_launched_from": "<string>",
//     "last_launched_to": "<string>",
//     "last_launched_by": "<string>",
//     "last_launched_on": "<string>",
//     "last_updated_by": "<string>",
//     "in_use_by": "<string>",
//     "tags": ["<string>"],
//     "created_by": "<string>",
//     "password_protected": <boolean>,
//     "password_restricted": [
    //     "profile_move",
    //     "profile_clone",
    //     "profile_start",
    //     "profile_export",
    //     "profile_update",
    //     "profile_data_change"
// ]
//     "notes": "<string>"
//     "sort": "<string>"
// }

```

Saved example: Search Done — HTTP 200
Top-level response keys: status, data
Data keys: profiles, total_count
Envelope http_code: 200

### Profile Management / Profile Remove

ID: `46206122-125a1f70-1490-42d5-a5a7-c51a61e97a5c`

`POST https://api.multilogin.com/profile/remove`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Remove profiles. Setting the value of `permanently` allows managing profile deletion. Deleting with `False` allows recovering deleted profiles when needed.

Check out **Params** to see what each key-value pair is about. To copy the example request body, please navigate to **Body**.

**Required parameters for Strict mode:**

``` json
{
  "ids": [
    "<string>"
  ],
  "permanently": <boolean>
}

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. Specify the ID of the profile to be deleted. |
| permanently | True | `Required`. Specify the value to delete profiles perminantly or not. Defaults to `false`. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "ids": [
    "<string>"
  ],
  "permanently": <boolean>
}
```

Saved example: Profile Deleted — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Profile Management / Profile Update

ID: `46206122-ba7cc00f-18ca-49ed-82b7-92d796d41ba7`

`POST https://api.multilogin.com/profile/update`

Update a profile. Fingerprint parameters need providing only if flags set to `Custom`.

Check out **Params** to see what each key-value pair is about. To copy the example request body, please navigate to **Body**.

If you would like to avoid having your profiles updated to the latest available core, specify `auto_update_core` (`true` or `false`). Updating existing profiles to a specific core version is not supported.

If you update an existing profile, created with `auto_update_core: false`, `auto_update_core: false` still has to be specified in the request. Otherwise, `auto_update_core` will be changed to `true`.

**NB:**

- **It is recommended to use the default values, which keep your browser cores up-to-date. Multilogin does not bear any responsability for ban or detection-related issues if profiles have a dated core version.**
    
- **If you update an existing profile, created with** **`auto_update_core: false`**, **`auto_update_core: false`** **still has to be specified in the request. Otherwise,** **`auto_update_core`** **will be changed to** **`true`**.
    

**Required parameters:**

``` json
{
    "name": "<string>",
    "profile_id": "<string>",
    "parameters": {
        "flags": {
            "audio_masking": "value",
            "fonts_masking": "value",
            "geolocation_masking": "value",
            "geolocation_popup": "value",
            "graphics_masking": "value",
            "graphics_noise": "value",
            "localization_masking": "value",
            "media_devices_masking": "value",
            "navigator_masking": "value",
            "ports_masking": "value",
            "proxy_masking": "value",
            "screen_masking": "value",
            "timezone_masking": "value",
            "webrtc_masking": "value",
        },
        "storage": {
            "is_local": <boolean>,
            "save_service_worker": <boolean>
        },
        "fingerprint": {}
}

 ```

The number of parameters in `fingerprint` may vary depending on the flag values passed in the request body.<p><strong>ISP proxies:</strong> to attach an MLX-managed ISP proxy, set <code>parameters.proxy.isp_ip_id</code> to the full proxy id returned by <strong>List ISP Proxies</strong> (Proxy folder) and send <code>"host": ""</code> alongside it - the <code>host</code> key must be present, but its value is ignored: connection details and credentials are resolved server-side from the registry when the profile starts. <code>type</code> / <code>port</code> / <code>username</code> / <code>password</code> can be omitted; a supplied <code>type</code> is ignored - the protocol comes from the registry.</p><p>Minimal proxy object:</p><pre><code>"proxy": { "host": "", "isp_ip_id": "&lt;uuid&gt;" }</code></pre><p>Attaching an IP already assigned to another profile returns <code>409</code>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| auto_update_core | True | `Optional`. Setting to True allows passing "core_version" and "core_minor_version". |
| core_version | True | `Optional`. Cannot specify the version that is 6 versions older then the current latest one. |
| core_minor_version | True | `Optional`. Specify the minor version based on its availability. |
| profile_id | True | `Required`. Specify the ID of the profile to be updated. |
| name | True | `Required`. Name your profiles. |
| tags | True | `Optional`. Specify tags. Max number is 10. |
| parameters | True | `Required`. Specify parameters for your profiles. `flags`, `fingerprint`, `storage` **are required** for **parameters**. |
| flags | True | `Required`. Specify flags for your profiles. `webrtc_masking, proxy_masking, geolocation_popup, audio_masking, graphics_noise, ports_masking, navigator_masking, localization_masking, timezone_masking, graphics_masking, fonts_masking, media_devices_masking, screen_masking, geolocation_masking` **are required** for **parameters**. |
| webrtc_masking | True | `Required` for `flags`. |
| audio_masking, graphics_noise, ports_masking | True | `Required` for `flags`. |
| proxy_masking | True | `Required` for `flags`. |
| geolocation_popup | True | `Required` for `flags`. |
| navigator_masking, localization_masking, timezone_masking, graphics_masking, fonts_masking, media_devices_masking, screen_masking | True | `Required` for `flags`. |
| geolocation_masking | True | `Required` for `flags`. |
| auto_update_core | True | `Optional`. You can skip specifying the value since your profiles will be updated to the latest core by default each time it is launched. |
| quic_mode | True | `Optional` for `flags`. `disabled` by default. |
| canvas_noise | True | `Optional` for `flags`. The value is set based on the value of `graphics_noise` by default. To set a specific value for `canvas_noise`, include `canvas_noise` in your request body. |
| startup_behavior | True | `Optional` for `flags`. `recover` is set by default and allows opening profiles with the tabs from the last session. `custom` opens up profiles with provided custom pages in `custom_start_urls`. |
| fingerprint | True | `Required` for `parameters`. Specify fingerprints of your profiles if flags are set to `Custom`. |
| hardware_concurrency | True | `Required` for `navigator`. Specify the value for `hardware_concurrency` if the flag is `Custom`. |
| user_agent | True | `Required` for `navigator`. Specify the value for `user-agent`. |
| platform | True | `Required` for `navigator`. Specify the value for `platform` if the flag is `Custom`. |
| os_cpu | True | `Optional` for `navigator`. Specify the value for `os_cpu`if the flag is `Custom`. |
| accept_languages | True | `Required` for `localization`. Specify the value for `accept_languages` if the flag is `Custom`. |
| languages | True | `Required` for `localization`. |
| locale | True | `Required` for `localization`. Pass an empty string. |
| zone | True | `Required` for `timezone` Specify the value for `zone`. |
| vendor | True | `Required` for `graphic`. Specify the value for `vendor` if the flag is `Custom`. |
| renderer | True | `Required` for `graphic`. Specify the value for `renderer` if the flag is `Custom`. |
| vendor_id | True | `Optional` for `graphic`. Specify the value for `vendor_id` if the flag is `Custom`. |
| renderer_id | True | `Optional` for `graphic`. Specify the value for `renderer_id` if the flag is `Custom`. |
| public_ip | True | `Required` for `webrtc`. Specify the value for `public_ip` if the flag is `Custom`. |
| audio_outputs | True | `Required` for `media_devices`. Specify the value for `audio_outputs` if the flag is `Custom`. |
| audio_inputs | True | `Required` for `media_devices`. Specify the value for `audio_inputs` if the flag is `Custom`. |
| video_inputs | True | `Required` for `media_devices`. Specify the value for `video_inputs` if the flag is `Custom`. |
| width | True | `Required` for `screen`. Specify the value for `width` if the flag is `Custom`. |
| height | True | `Required` for `screen`. Specify the value for `height` if the flag is `Custom`. |
| pixel_ratio | True | `Required` for `screen`. Specify the value for `pixel_ratio` if the flag is `Custom`. |
| accuracy | True | `Required` for `geolocation`. Specify the value for `accuracy` if the flag is `Custom`. |
| altitude | True | `Required` for `geolocation`. Specify the value for `altitude` if the flag is `Custom`. |
| latitude | True | `Required` for `geolocation`. Specify the value for `latitude` if the flag is `Custom`. |
| longitude | True | `Required` for `geolocation`. Specify the value for `longitude` if the flag is `Custom`. |
| ports | True | `Optional` for `fingerprint`. Specify the value for `ports` if the flag is `Custom`. |
| fonts | True | `Optional` for `fingerprint`. Specify the value for `fonts` if the flag is `Custom`. |
| cmd_params | True | `Optional` for `fingerprint`. Specify command line parameters for browsers. |
| is_local | True | `Required` for `storage`. |
| save_service_worker | True | `Optional` for `storage`. |
| proxy | True | `Optional` for `fingerprint`. Add a proxy to your profiles. |
| parameters.proxy.isp_ip_id | True | `Optional`. MLX-managed ISP proxy id - get it from `List ISP Proxies` in the Proxy folder. Send `"host": ""` alongside it (the key is required, the value is ignored); `type` / `port` / `username` / `password` can be omitted - connection details are resolved server-side. In this endpoint the proxy object lives under `parameters`. |
| save_traffic | True | `Optional` for `proxy`. `false` is set by default. When set to `true`,  disables the loading of images/videos saving the proxy traffic. |
| custom_start_urls | True | `Optional` for `fingerprint`. Specify custom URLs. Max amount is 5. |
| notes | True | `Optional`. Add notes to your profiles. Max length is 400 chars. |
| max_touch_points | True | `Optional` for `fingerprint` with `android` os. Default is 5. |

**Body template** (`text`; chưa phải payload runnable):

```text
{
    "profile_id": "<string>",
    "auto_update_core": <boolean>,  // Specify False to be able to pass "core_version" and "core_minor_version"
    "core_version": <integer>,
    "core_minor_version": <integer>,
    "name": "<string>",
    "parameters": {
        "flags": {
            "audio_masking": "<string>",
            "fonts_masking": "<string>",
            "geolocation_masking": "<string>",
            "geolocation_popup": "<string>",
            "graphics_masking": "<string>",
            "graphics_noise": "<string>",
            "localization_masking": "<string>",
            "media_devices_masking": "<string>",
            "navigator_masking": "<string>",
            "ports_masking": "<string>",
            "proxy_masking": "<string>",
            "screen_masking": "<string>",
            "timezone_masking": "<string>",
            "webrtc_masking": "<string>",
            "canvas_noise:": "<string>",
            "startup_behavior": "<string>",
        },
        "storage": {
            "is_local": <boolean>,
            "save_service_worker": <boolean>
        },
        "fingerprint": {
            "navigator": {
                "hardware_concurrency": <integer>,
                "platform": "<string>",
                "user_agent": "<string>",
                "os_cpu": "<string>"
            },
            "localization": {
                "languages": "<string>",
                "locale": "<string>",
                "accept_languages": "<string>"
            },
            "timezone": {
                "zone": "<string>"
            },
            "graphic": {
                "renderer": "<string>",
                "vendor": "<string>"
            },
            "webrtc": {
                "public_ip": "<string>"
            },
            "media_devices": {
                "audio_inputs": <integer>,
                "audio_outputs": <integer>,
                "video_inputs": <integer>
            },
            "screen": {
                "height": <integer>,
                "pixel_ratio": <double>,
                "width": <integer>
            },
            "geolocation": {
                "accuracy": <number>,
                "altitude": <number>,
                "latitude": <number>,
                "longitude": <number>
            },
            "ports": [
                <integer>,
            ],
            "fonts": [
                "<string>"
            ],
            "cmd_params": {
                "params": [
                    {
                        "flag": "<string>",
                        "value": "<boolean>"
                    }
                ]
            }
        },
        "proxy": {
            "host": "<string>",
            "type": "<string>",
            "port": <integer>,
            "username": "<string>",
            "password": "<string>",
            "save_traffic": "<boolean>",
            "isp_ip_id": "<string>"
        },
        "custom_start_urls": [
            "<string>"
        ]
    },
    "notes": "<string>"
}
```

Saved example: Profile Updated — HTTP 201
Top-level response keys: status, data
Envelope http_code: 200

### Profile Management / Profile Move

ID: `46206122-24f05210-76b4-4b88-8935-b451cf82f958`

`POST {{baseUrl}}/profile/move`

Move profiles to a specified folder.

**Required parameters:**

``` json
{
  "dest_folder_id": "<string>",
  "ids": [
    "<string>"
  ]
}

 ```

If a profile to move is password protected, use the following request body:

``` json
{
    "dest_folder_id": "{{FolderCreateID}}",
    "profiles": [
        {
            "profile_id": "{{ProfileMimic}}",
            "password": "{{ProfilePassword}}"
        }
    ]
}

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| dest_folder_id | True | `Required`. Specify the folder, to which profiles will be moved. |
| ids | True | `Required`. Provide a list of profiles to be moved. Max number of IDs is 20. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "dest_folder_id": "<string>",
  "ids": [
    "<string>"
  ]
}
```

Saved example: Profiles Moved — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Profile Management / Profile Partial Update

ID: `46206122-3f0ee19d-6f3b-4377-8e17-6f99c440124d`

`POST https://api.multilogin.com/profile/partial_update`

Update a profile partially according to your requirements. Fingerprint parameters need providing only if flags set to `Custom`.

Check out **Params** to see what each key-value pair is about. To copy the example request body, please navigate to **Body**.

If you would like to avoid having your profiles updated to the latest available core, specify `auto_update_core` (`true` or `false`) and a specific `core_version`. Updating existing profiles to a specific core version is not supported.

**NB:**

- **It is recommended to use the default values, which keep your browser cores up-to-date. Multilogin does not bear any responsability for ban or detection-related issues if profiles have a dated core version.**
    
- **If you update an existing profile, created with** **`auto_update_core: false`**, **`auto_update_core: false`** **still has to be specified in the request. Otherwise,** **`auto_update_core`** **will be changed to** **`true`**.
    

**Required parameters:**

``` json
{
    "profile_id": "<string>"
}

 ```

The number of parameters in `fingerprint` may vary depending on the flag values passed in the request body.<p><strong>ISP proxies:</strong> to attach an MLX-managed ISP proxy, set the <strong>top-level</strong> <code>proxy.isp_ip_id</code> (this endpoint takes <code>proxy</code> at the root of the body, not under <code>parameters</code>) to the full proxy id returned by <strong>List ISP Proxies</strong> (Proxy folder) and send <code>"host": ""</code> alongside it - the <code>host</code> key must be present, but its value is ignored: connection details and credentials are resolved server-side from the registry when the profile starts. <code>type</code> / <code>port</code> / <code>username</code> / <code>password</code> can be omitted; a supplied <code>type</code> is ignored - the protocol comes from the registry.</p><p>If the profile's proxy is currently disabled, also set <code>parameters.flags.proxy_masking</code> to <code>"custom"</code> - otherwise the attached proxy is excluded from the profile's launch configuration. Minimal body:</p><pre><code>{
  "profile_id": "&lt;uuid&gt;",
  "proxy": { "host": "", "isp_ip_id": "&lt;uuid&gt;" },
  "parameters": { "flags": { "proxy_masking": "custom" } }
}</code></pre><p>Attaching an IP already assigned to another profile returns <code>409</code>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | True | `Required`. Specify the ID of the profile to be updated. |
| name | True | `Optional`. Name your profiles. |
| auto_update_core | True | `Optional`. You can skip specifying the value since your profiles will be updated to the latest core by default each time it is launched. |
| core_minor_version | True | `Optional`. Specify the minor version based on its availability. |
| core_version | True | `Optional`. Cannot specify the version that is 6 versions older then the current latest one. |
| tags | True | `Optional`. Specify tags. Max number is 10. |
| proxy | True | `Optional` for `fingerprint`. Add a proxy to your profiles. |
| proxy.isp_ip_id | True | `Optional`. MLX-managed ISP proxy id - get it from `List ISP Proxies` in the Proxy folder. Send `"host": ""` alongside it (the key is required, the value is ignored); `type` / `port` / `username` / `password` can be omitted - connection details are resolved server-side. In this endpoint the proxy object is TOP-LEVEL (not under `parameters`). If the profile's proxy is disabled, also set `parameters.flags.proxy_masking: "custom"`. |
| save_traffic | True | `Optional` for `proxy`. `false` is set by default. When set to `true`,  disables the loading of images/videos saving the proxy traffic. |
| custom_start_urls | True | `Optional` for `fingerprint`. Specify custom URLs. Max amount is 5. |
| notes | True | `Optional`. Add notes to your profiles. Max length is 400 chars. |
| parameters | True | `Optional`. |
| flags | True | `Optional`. |
| webrtc_masking | True | `Optional`. |
| audio_masking, graphics_noise, ports_masking | True | `Optional`. |
| proxy_masking | True | `Optional`. |
| geolocation_popup | True | `Optional`. |
| navigator_masking, localization_masking, timezone_masking, graphics_masking, fonts_masking, media_devices_masking, screen_masking | True | `Optional`. |
| geolocation_masking | True | `Optional`. |
| quic_mode | True | `Optional` for `flags`. `disabled` by default. |
| canvas_noise | True | `Optional` for `flags`. The value is set based on the value of `graphics_noise` by default. To set a specific value for `canvas_noise`, include `canvas_noise` in your request body. |
| startup_behavior | True | `Optional` for `flags`. `recover` is set by default and allows opening profiles with the tabs from the last session. `custom` opens up profiles with provided custom pages in `custom_start_urls`. |
| is_local | True | `Required` for `storage`. |
| save_service_worker | True | `Optional` for `storage`. |
| fingerprint | True | `Required` for `parameters`. Specify fingerprints of your profiles if flags are set to `Custom`. |
| hardware_concurrency | True | `Required` for `navigator`. Specify the value for `hardware_concurrency` if the flag is `Custom`. |
| user_agent | True | `Required` for `navigator`. Specify the value for `user-agent`. |
| platform | True | `Required` for `navigator`. Specify the value for `platform` if the flag is `Custom`. |
| os_cpu | True | `Optional` for `navigator`. Specify the value for `os_cpu`if the flag is `Custom`. |
| accept_languages | True | `Required` for `localization`. Specify the value for `accept_languages` if the flag is `Custom`. |
| languages | True | `Required` for `localization`. |
| locale | True | `Required` for `localization`. Pass an empty string. |
| zone | True | `Required` for `timezone` Specify the value for `zone`. |
| vendor | True | `Required` for `graphic`. Specify the value for `vendor` if the flag is `Custom`. |
| renderer | True | `Required` for `graphic`. Specify the value for `renderer` if the flag is `Custom`. |
| vendor_id | True | `Optional` for `graphic`. Specify the value for `vendor_id` if the flag is `Custom`. |
| renderer_id | True | `Optional` for `graphic`. Specify the value for `renderer_id` if the flag is `Custom`. |
| public_ip | True | `Required` for `webrtc`. Specify the value for `public_ip` if the flag is `Custom`. |
| audio_outputs | True | `Required` for `media_devices`. Specify the value for `audio_outputs` if the flag is `Custom`. |
| audio_inputs | True | `Required` for `media_devices`. Specify the value for `audio_inputs` if the flag is `Custom`. |
| video_inputs | True | `Required` for `media_devices`. Specify the value for `video_inputs` if the flag is `Custom`. |
| width | True | `Required` for `screen`. Specify the value for `width` if the flag is `Custom`. |
| height | True | `Required` for `screen`. Specify the value for `height` if the flag is `Custom`. |
| pixel_ratio | True | `Required` for `screen`. Specify the value for `pixel_ratio` if the flag is `Custom`. |
| accuracy | True | `Required` for `geolocation`. Specify the value for `accuracy` if the flag is `Custom`. |
| altitude | True | `Required` for `geolocation`. Specify the value for `altitude` if the flag is `Custom`. |
| latitude | True | `Required` for `geolocation`. Specify the value for `latitude` if the flag is `Custom`. |
| longitude | True | `Required` for `geolocation`. Specify the value for `longitude` if the flag is `Custom`. |
| ports | True | `Optional` for `fingerprint`. Specify the value for `ports` if the flag is `Custom`. |
| fonts | True | `Optional` for `fingerprint`. Specify the value for `fonts` if the flag is `Custom`. |
| cmd_params | True | `Optional` for `fingerprint`. Specify command line parameters for browsers. |
| max_touch_points | True | `Optional` for `fingerprint` with `android` os. Default is 5. |

**Body template** (`text`; chưa phải payload runnable):

```text
{
    "profile_id": "<string>",
    "name": "<string>",
    "auto_update_core": <boolean>,  // Specify False to be able to pass "core_version" and "core_minor_version"
    "core_version": <integer>,
    "core_minor_version": <integer>,
    "proxy": {
        "host": "<string>",
        "type": "<string>",
        "port": <integer>,
        "username": "<string>",
        "password": "<string>",
        "save_traffic": "<boolean>",
        "isp_ip_id": "<string>"
    },
    "custom_start_urls": [
        "<string>"
    ],
    "notes": "<string>",
    "parameters": {
        "flags": {
            "audio_masking": "<string>",
            "fonts_masking": "<string>",
            "geolocation_masking": "<string>",
            "geolocation_popup": "<string>",
            "graphics_masking": "<string>",
            "graphics_noise": "<string>",
            "localization_masking": "<string>",
            "media_devices_masking": "<string>",
            "navigator_masking": "<string>",
            "ports_masking": "<string>",
            "proxy_masking": "<string>",
            "screen_masking": "<string>",
            "timezone_masking": "<string>",
            "webrtc_masking": "<string>",
            "canvas_noise": "<string>",
            "startup_behavior": "<string>"
        },
        "storage": {
            "is_local": <boolean>,
            "save_service_worker": <boolean>
        },
        "fingerprint": {
            "navigator": {
                "hardware_concurrency": <integer>,
                "platform": "<string>",
                "user_agent": "<string>",
                "os_cpu": "<string>"
            },
            "localization": {
                "languages": "<string>",
                "locale": "<string>",
                "accept_languages": "<string>"
            },
            "timezone": {
                "zone": "<string>"
            },
            "graphic": {
                "renderer": "<string>",
                "vendor": "<string>"
            },
            "webrtc": {
                "public_ip": "<string>"
            },
            "media_devices": {
                "audio_inputs": <integer>,
                "audio_outputs": <integer>,
                "video_inputs": <integer>
            },
            "screen": {
                "height": <integer>,
                "pixel_ratio": <double>,
                "width": <integer>
            },
            "geolocation": {
                "accuracy": <number>,
                "altitude": <number>,
                "latitude": <number>,
                "longitude": <number>
            },
            "ports": [
                <integer>,
            ],
            "fonts": [
                "<string>"
            ],
            "cmd_params": {
                "params": [
                    {
                        "flag": "<string>",
                        "value": "<string>"
                    }
                ]
            }
        }
    }
}
```

Saved example: Profile Updated — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Profile Management / Profile Restore

ID: `46206122-a53bd3de-8d19-4d38-9c62-c863cb96f3ec`

`POST https://api.multilogin.com/profile/restore`

Restore profiles deleted with the `permanently` value set to `False`.

Check out **Params** to see what each key-value pair is about. To copy the example request body, please navigate to **Body**.

**Required parameters:**

``` json
{
  "ids": [
    "<string>"
  ]
}

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. Specify the ID of the profile you would like to restore. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "ids": [
    "<string>"
  ]
}
```

Saved example: Profile Restored — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Profile Management / Profile Metas

ID: `46206122-77349d1b-d18a-4145-9c6e-79dd586d8558`

`POST https://api.multilogin.com/profile/metas`

Fetch metas of profiles. The number of parameters depends on the data specified when profiles have been created.

Check out **Params** to see what each key-value pair is about. To copy the example request body, please navigate to **Body**.

**Required parameters:**

``` json
{
  "ids": [
    "<string>"
  ]
}

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. Specify the ID of the profile, which metas you would like to fetch. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "ids": [
    "<string>"
  ]
}
```

Saved example: Profile Meta Fetched — HTTP 200
Top-level response keys: status, data
Data keys: profiles
Envelope http_code: 200

### Profile Management / Profile Summary

ID: `46206122-511119dc-dd49-4f5b-bd06-7328b599389a`

`GET https://api.multilogin.com/profile/summary?meta_id=uuid`

Fetch profile fingerprints.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| meta_id | False | `Required`. Specify the profile id. |

**Body template** (`json`; chưa phải payload runnable):

```text

```

Saved example: Profile Summary Fetched — HTTP 200
Top-level response keys: status, data
Data keys: fonts, geolocation, graphic, localization, masking_options, media_devices, navigator, ports, screen, timezone, webrtc
Envelope http_code: 200

### Profile Management / Profile Clone

ID: `46206122-3439fc2c-0095-4632-bda2-d7d55b6f68f0`

`POST https://api.multilogin.com/profile/clone`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Clone profiles.

Check out **Params** to see what each key-value pair is about. To copy the example request body, please navigate to **Body**.

**Required parameters for Strict mode:**

``` json
{
  "profile_id": "<string>",
  "times": <integer>
}

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | True | `Required`. Specify the ID of the original profile. |
| times | True | `Required`. Specify the number of profiles you would like to clone. Defaults to `1`. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "profile_id": "<string>",
  "times": <integer>
}
```

Saved example: Profile Cloned — HTTP 200
Top-level response keys: status, data
Data keys: ids
Envelope http_code: 200

### Profile Management / Profile Convert

ID: `46206122-78add591-dba8-41d8-8561-23cf43712a91`

`POST https://launcher.mlx.yt:45001/api/v1/profile/:profile_id/convert`

Check out **Params** to see what each key-value pair is about. To copy the example request body, please navigate to **Body**.

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | False | `Required`. Specify the ID of the original profile. |

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| convert_to_local | True | `Required`. True if you want to convert from cloud to local and false otherwise. |
| workspace_id | True | `Required`. Specify the workspace id. |
|  | True |  |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "workspace_id": "<string>",
    "convert_to_local" : <boolean>
}
```

Saved example: Profile Convert — HTTP 200
Top-level response keys: status
Envelope http_code: 200

### Profile Management / Screen Resolution

ID: `46206122-2223a907-b701-400d-b30b-ad4b0707568f`

`GET https://api.multilogin.com/fpb/resolutions`

Fetch a list of available screen resolutions.

Saved example: Screen Resolution Fetched — HTTP 200
Top-level response keys: status, data
Data keys: resolutions
Envelope http_code: 200

### Profile Management / Tag Create

ID: `46206122-75122aa3-1547-41c7-87e2-d270bc9b62ec`

`POST https://api.multilogin.com/tag/create`

Create a tag. Default tag color is `gray`.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| tags | True | `Required`. |
| color | True | `Optional`. Specify the tag color. Default tag color is `gray`. |
| name | True | `Required`. Specify the tag name. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "tags": [
        {
            "name": "<string>",
            "color": "<string>"
        }
    ]
}
```

Saved example: Tag Create — HTTP 201
Top-level response keys: status, data
Data keys: ids
Envelope http_code: 201

### Profile Management / Tag Update

ID: `46206122-c8213f49-8f27-46dd-9a46-650ed9ed4dd2`

`POST https://api.multilogin.com/tag/update`

Update an existing tag.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| tag_id | True | `Required`. Specify the tag id. |
| color | True | `Required`. Specify the new tag color. |
| name | True | `Required`. Specify the new tag name. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "tag_id": "<string>",
    "color": "<string>",
    "name": "<string>"
}
```

Saved example: Tag Update — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Profile Management / Tag Remove

ID: `46206122-653fdf2c-2b9f-497e-8b07-77229b07e16c`

`POST https://api.multilogin.com/tag/remove`

Remove a tag.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. Specify the list of tags. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "ids": [
        "<string>"
    ]
}
```

Saved example: Tag Remove — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Profile Management / Tag Assign

ID: `46206122-e827150f-dce9-4854-8523-1a84065f7f31`

`POST https://api.multilogin.com/tag/assign`

Use tags in a specific profile.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | True | `Required`. Specify the profile ID. |
| tags | True | `Required`. Specify the list of tags IDs. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "profile_id": "<string>",
    "tags": [
        "<string>"
    ]
}
```

Saved example: Tag Assign — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Profile Management / Tag Search

ID: `46206122-f87841f7-faf4-43c8-a52d-f2dc8040fe20`

`POST https://api.multilogin.com/tag/search`

Search tags.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| search_text | True | `Required`. Specify the tag name. Can be an empty string. |
| offset | True | `Required`. Specify the offset. |
| limit | True | `Required`. Specify the limit. |
| order_by | True | `Optional`. Specify the order. `name` by default. |
| sort | True | `Optional`. Specify the sorting. `asc` by default. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "search_text": "<string>",
    "limit": <integer>,
    "offset": <integer>,
    "order_by": "<string>", // optional
    "sort": "<string>" // optional
}
```

Saved example: Tag Assign — HTTP 200
Top-level response keys: status, data
Data keys: tags, total_count
Envelope http_code: 200

### Profile Management / Set Profile Password

ID: `46206122-fb5efd12-574a-494c-8b43-dfe00d8f17e9`

`POST https://api.multilogin.com/profile/security/enable`

Set password to a specific profile. Password must be at least 7 characters long and include at least one uppercase letter, one number, and one special character.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profiles | True | `Required`. |
| profile_id | True | `Required`. |
| password | True | `Required`. Password must be at least 7 characters long and include at least one uppercase letter, one number, and one special character |
| confirm_password | True | `Required`. Password must be at least 7 characters long and include at least one uppercase letter, one number, and one special character |
| restricted | True | `Required`. Specify restricted actions. When sending an empty array, all the actions are restricted. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "profiles": [
        {
            "profile_id": "<string>",
            "password": "<string>",
            "confirm_password": "<string>",
            "restricted": [
                    "profile_move",
                    "profile_clone",
                    "profile_start",
                    "profile_export",
                    "profile_update",
                    "profile_data_change"
            ]
        }
    ]
}
```

Saved example: Set Profile Password — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Profile Management / Log In Profile

ID: `46206122-76aed15b-469b-4dcb-a12e-ea01ac9e367e`

`POST https://api.multilogin.com/profile/login`

Log into a profile. After logging, a JWT has to be passed in the headers of any subsequent call to unlock a restricted action.

If starting profile or any other action was restricted, the headers of the start profile or any other call would have the following extra key:

``` json
'X-Profile-Authentication: Bearer your_profile_jwt'

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | True | `Required`. |
| password | True | `Required`. Password must be at least 7 characters long and include at least one uppercase letter, one number, and one special character |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "password": "<string>",
  "profile_id": "<string>"
}
```

Saved example: Log In Profile — HTTP 200
Top-level response keys: status, data
Data keys: token
Envelope http_code: 200

### Profile Management / Remove Password

ID: `46206122-108ef574-c1aa-4d63-a092-9a27975a970c`

`POST https://api.multilogin.com/profile/security/disable`



**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_ids | True | `Required`. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "profile_ids": [
        "<string>"
    ]
}
```

Saved example: Remove Password — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Browser Profile Data / Unlock Locked Profiles

ID: `46206122-c0429b19-f40f-432f-bd19-355d84d4e210`

`GET https://api.multilogin.com/bpds/profile/unlock_profiles`

Unlocks all the locked.

To unlock specific profiles, pass the IDs in the request body. Sending a request without any request body unlocks all the profiles.

**It is important to close all the locked profiles before calling this endpoint!**

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Optional`. Specify the ID of the profile to unlock. To unlock all the profile, call the endpoint without the body. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "ids": ["<string>"]
}
```

Saved example: Profiles Unlocked — HTTP 500
Top-level response keys: status, data
Envelope http_code: 200

### Proxy / Generate Proxy

ID: `46206122-fbd6be66-036e-455e-bfbc-8ec53691fbc7`

`GET https://api.multilogin.com/proxynm/connection_url?country=us&protocol=socks5&session_type=sticky`

<p>Generate proxy connection URLs from the provided settings.</p><p>Each returned string is a ready-to-use connection URL in the <code>host:port:username:password</code> format. The port depends on the protocol: <code>1080</code> for socks5, <code>8080</code> for http.</p><p>Use <code>session_type=sticky</code> to keep the same exit IP for the session, or <code>rotating</code> to get a new IP per request. Use <code>count</code> to generate several URLs in one call.</p><p><strong>NB: the previous endpoint <code>POST https://profile-proxy.multilogin.com/v1/proxy/connection_url</code> is deprecated - use this one.</strong></p><p>Check out <strong>Params</strong> to see what each parameter is about.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| country | False | `Required`. Proxy country code, e.g. `us` |
| protocol | False | `Required`. Proxy protocol: `http` or `socks5` |
| session_type | False | `Required`. Session type: `sticky` (keeps the same exit IP, adds a session id to the username) or `rotating` |
| region | True | `Optional`. Proxy region |
| city | True | `Optional`. Proxy city |
| ip_ttl | True | `Optional`. Sticky session IP lifetime |
| count | True | `Optional`. Amount of connection URLs to generate (1-100, default 1) |
| connection_type | True | `Optional`. Connection type for the results: `residential` (default) or `mobile` |
| isp | True | `Optional`. Proxy ISP |

Saved example: Connection URLs Retrieved — HTTP 200
Top-level response keys: status, data
Data keys: connection_urls
Envelope http_code: 200

### Proxy / Fetch Proxy Data

ID: `46206122-4ac3db14-3b5d-4476-a492-cda474c5b8bc`

`GET https://api.multilogin.com/proxynm/user`

<p>Fetch proxy-related data for the current workspace: the remaining proxy traffic and billing identifiers.</p><p><code>traffic</code> is the remaining allowance in bytes.</p><p><strong>NB: the previous endpoint <code>GET https://profile-proxy.multilogin.com/v1/user</code> is deprecated - use this one.</strong></p><p>This endpoint takes no parameters.</p>

Saved example: Proxy Data Fetched — HTTP 200
Top-level response keys: status, data
Data keys: billing_id, traffic, workspace_id
Envelope http_code: 200

### Proxy / List ISP Proxies

ID: `46206122-3410f031-4802-446c-8a50-6945eb46965b`

`GET https://api.multilogin.com/proxynm/isp/proxies`

<p>List the ISP proxies of your workspace with their full IDs, assignment and expiry state.</p><p><code>ip_id</code> is the full ISP proxy id: pass it as <code>parameters.proxy.isp_ip_id</code> in <strong>Profile Create</strong> / <strong>Profile Update</strong>, as top-level <code>proxy.isp_ip_id</code> in <strong>Profile Partial Update</strong> or as <code>isp_ip_id</code> in the mobile profile <code>proxy_config</code>. The Billing UI shows only the first characters of the id - this endpoint returns the full value.</p><p><code>status</code>: <code>active</code> or <code>expired</code>. <code>assignment_state</code>: <code>available</code> or <code>assigned</code>; for assigned proxies <code>profile_id</code> and <code>profile_type</code> (<code>browser</code> | <code>mobile</code>) identify the owning profile.</p><p>The response never includes connection credentials (host / port / username / password) - they are resolved server-side when a profile with the ISP proxy starts.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| country | True | `Optional`. Filter by country code - exact match, lowercase (e.g. `us`) |

Saved example: ISP Proxies Listed — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Pre-made Cookies / Target Website List

ID: `46206122-8aef1d76-52aa-44db-bb8b-bffc1ab94a59`

`GET https://cookies.multilogin.com/api/v1/cookies/metadata/websites`

Get a list of the target websites available as well as the keyword for the **target_website.**

Saved example: Target Website List — HTTP 200
Top-level response keys: data, status
Envelope http_code: 200

### Pre-made Cookies / Create Cookies Metadata

ID: `46206122-ca57a996-86ec-4bc4-aa61-54b6681bfec2`

`POST https://cookies.multilogin.com/api/v1/cookies/metadata`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Create cookies metadata for a given profile. The endpoint does not create cookies by itself. It serves to add cookies-related metadata into a profile. This profile cookies metadata will be used by the server to provide the right cookies for a given target website.

**Required parameters for Strict mode:**

``` json
{
  "profile_id": "<string>",
  "target_website": "<string>"
}

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | True | `Required` |
| target_website | True | `Required`. Defaults to `mix`. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "profile_id": "<string>",
  "target_website": "<string>"
}
```

Saved example: Create Cookies Metadata — HTTP 201
Top-level response keys: data, status
Data keys: profile_id
Envelope http_code: 201

### Pre-made Cookies / Cookies List

ID: `46206122-42b77ead-ac7b-455c-aa83-006367991895`

`GET https://cookies.multilogin.com/api/v1/cookies/<your profile id>`

Fetch cookies for a given profile, based on the target website in the cookies metatada created by `POST https://cookies.multilogin.com/api/v1/cookies/metadata.`

Note that cookies returned in the response may not be the same ones to be imported into your browser profiles. The endpoint returns cookies randomly, based on the target website.

Saved example: Cookies List — HTTP 200
Top-level response keys: data, status
Data keys: cookies
Envelope http_code: 200

### Pre-made Cookies / Update Cookies Metadata

ID: `46206122-51e6a0ea-4759-4f6d-a260-c46e7b4159d2`

`PUT https://cookies.multilogin.com/api/v1/cookies/metadata`

This endpoint supports both Strict and Non-Strict modes. In Strict mode, all required parameters must be explicitly specified. In contrast, Non-Strict mode allows for faster usage by applying default values to any unspecified parameters. Default values will be visible for each parameter.

Update cookies metadata to change the target website.

**Required parameters for Strict mode:**

``` json
{
  "profile_id": "<string>",
  "target_website": "<string>"
}

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | True | `Required` |
| target_website | True | `Required`. Defaults to `mix`. |
| additional_website | True | `Optional` |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "profile_id": "<string>",
  "target_website": "<string>",
   "additional_website": "<string>"
}
```

Saved example: Update Cookies Metadata — HTTP 200
Top-level response keys: status
Envelope http_code: 200

### Script Runner / Start Browser Profile with Selenium

ID: `46206122-81faae91-0c7c-4d5b-8d77-1923659aeb45`

`GET https://launcher.mlx.yt:45001/api/v1/profile/f/:folder_id/p/:profile_id/start?automation_type=selenium`

Start a browser profile with `automation_type=selenium`

The endpoint will return a port for automation in the response message, that will be used to start Script Runner on active profiles.

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| folder_id | False | `Required`. Specify the ID of the folder where the profile to launch is stored. |
| profile_id | False | `Required`. Specify the ID of the profile to launch. |

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| automation_type | False |  |

Saved example: Profile Started — HTTP 200
Top-level response keys: status
Envelope http_code: 200

### Script Runner / Start Script Runner

ID: `46206122-a959693f-fbd9-4326-9246-2460f81fe103`

`POST https://launcher.mlx.yt:45001/api/v1/run_script`

Run scripts on one or multiple profiles. The endpoint allows executing scripts in two ways:

1. **executing scripts on running/active profiles.**  
    To use this method, start a profile with [GET Start Browser Profile](https://documenter.getpostman.com/view/28533318/2s946h9Cv9#292fe0f0-5b24-4dae-bcec-bf21b0d96367) with Seleinum and send a request to `POST Start Runner`, passing the profile IDs in the request body. Profiles remains open after the script has been executed.
    
2. **executing scripts along with starting profiles.**  
    To use this method, send a request to `POST Start Runner`, passing the profile IDs in the request body. Profiles closes after the script has been executed.
    

The value of `script_file` is the name of the .py file relative to the folder.

Scripts are stored by default in the following directories:

- Windows: `C:\Users\%username%\mlx\deps\scripts`
    
- macOS: `/Users/%username%/mlx/scripts`
    
- Linux: `/home/%username%/mlx/scripts`
    

**Required parameters:**

``` json
{
    "script_file": "<string>",
    "profile_ids": [
        {
            "profile_id": "<string>"
        }
    ]
}

 ```

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| script_file | True | `Required`. Specify the scrip file to execute. |
| profile_ids | True | `Required`. Specify profiles and launch mode. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "script_file": "<string>",
    "profile_ids": [
        {
            "profile_id": "<string>",
            "is_headless": <boolean>
        }
    ]
}
```

Saved example: Script Runner Started — HTTP 200
Top-level response keys: data, status
Envelope http_code: 200

### Script Runner / Stop Script Runner

ID: `46206122-30de9b08-25d3-4521-a2b9-579829a6af05`

`POST https://launcher.mlx.yt:45001/api/v1/profile/stop_script`

Stop scripts from executing.

**Required parameters:**

``` json
{
    "profile_ids": [
        "<string>"
    ]
}

 ```

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "profile_ids": [
        "<string>"
    ]
}
```

Saved example: Script Stopped — HTTP 200
Top-level response keys: data, status
Envelope http_code: 200

### Script Runner / Script List

ID: `46206122-82efa0c6-5768-4386-9b2a-9524518ecfe6`

`GET https://launcher.mlx.yt:45001/api/v1/scripts`

Return a list of saved scripts.

Scripts are stored by default in the following directories:

- Windows: `C:\Users\%username%\mlx\deps\scripts`
    
- macOS: `/Users/%username%/mlx/deps/scripts`
    
- Linux: `/home/%username%/mlx/deps/scripts`

Saved example: Script List — HTTP 200
Top-level response keys: data, status
Envelope http_code: 200

### Profile Import/Export / Profile Export

ID: `46206122-3b9c3f2e-91a6-41ea-b4ce-a55e898e4efa`

`POST https://launcher.mlx.yt:45001/api/v1/profile/:profile_id/export`

Export a profile.

Profiles are exported by default to the following directories:

- Windows: `C:\Users\%username%\mlx\exports`
    
- macOS: `/Users/%username%/mlx/exports`
    
- Linux: `/home/%username%/mlx/exports`

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | False | `Required`. Specify the profile ID to export. |

Saved example: Export Profile — HTTP 200
Top-level response keys: data, status
Data keys: export_id, export_path, message, profile_id, status, timestamp
Envelope http_code: 200

### Profile Import/Export / Export Status by Profile

ID: `46206122-9f5242eb-4de5-4c02-aadf-0fce94abaf32`

`GET https://launcher.mlx.yt:45001/api/v1/profile/exports/:export_id/status`

Get status of profile export by export ID.

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| export_id | False | `Required`. Specify the export operation ID. |

Saved example: Export Status by Profile — HTTP 200
Top-level response keys: data, status
Data keys: export_id, export_path, message, profile_id, status, timestamp
Envelope http_code: 200

### Profile Import/Export / Export Status All

ID: `46206122-b846df18-45b1-49ea-9506-a63b3d3ec5bb`

`GET https://launcher.mlx.yt:45001/api/v1/profile/exports/statuses`

Get status of all export profile operations.

Saved example: Export Status by Profile — HTTP 200
Top-level response keys: data, status
Data keys: statuses
Envelope http_code: 200

### Profile Import/Export / Profile Import

ID: `46206122-92939555-fa96-4ecf-ac84-b8f58858dac1`

`POST https://launcher.mlx.yt:45001/api/v1/profile/import`

Import a profile.

Specify `is_local` to indicate a profile type (local or cloud).

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| import_path | True | `Required`. Specify the path to the profile in the zip format. |
| is_local | True | `Required`. Specify the type of the imported profile. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "import_path": "<string>",
    "is_local": <boolean>
}
```

Saved example: Profile Import — HTTP 200
Top-level response keys: data, status
Data keys: export_id, import_id, import_path, message, status, timestamp
Envelope http_code: 200

### Profile Import/Export / Import Status by Profile

ID: `46206122-4f267c0c-93ae-4674-85a4-e0987bbb7688`

`GET https://launcher.mlx.yt:45001/api/v1/profile/imports/:import_id/status`

Get status of profile import by export ID.

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| import_id | False | `Required`. Specify the import operation ID. |

Saved example: Import Status by Profile — HTTP 200
Top-level response keys: data, status
Data keys: export_id, extracted_path, import_id, import_path, message, new_profile_id, status, timestamp
Envelope http_code: 200

### Profile Import/Export / Import Status All

ID: `46206122-b01a02db-0c96-41aa-87e1-4c3bc800643d`

`GET https://launcher.mlx.yt:45001/api/v1/profile/imports/statuses`

Get status of profile import operations.

Saved example: Import Status All — HTTP 200
Top-level response keys: data, status
Data keys: statuses
Envelope http_code: 200

### Object Storage / Upload Object

ID: `46206122-c09bff17-e601-472e-96f0-be600356a428`

`POST https://launcher.mlx.yt:45001/api/v1/object_storage/upload`

This endpoint allows you to upload an object to the storage.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| object_type_id | True | `Required`. The ID of the object type |
| object_path | True | `Required`. The path of the object. |
| storage_type | True | `Required`. The type of storage. |
| object_meta | True | `Optional`. The object meta data. |
| encrypt | True | `Optional`. Encryption value |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "object_type_id": "<string>",
    "object_path": "<string>",
    "storage_type": "<value>",
    "object_meta": "{\"meta1\":{\"key1\":\"value1\",\"key2\":\"value3\"}}",
    "encrypt": "<boolean>"
}
```

Saved example: Upload Object — HTTP 200
Top-level response keys: status, data
Data keys: meta_id
Envelope http_code: 0

### Object Storage / Create and Upload

ID: `46206122-0938fb11-c19a-4fbd-8f5e-4f9ad107744b`

`POST https://launcher.mlx.yt:45001/api/v1/object_storage/create_and_upload`

This endpoint allows you to upload an object to the storage. It is designed to facilitate the creation and uploading of various types of objects, enabling users to manage their data efficiently.

#### Request Body

- `object_name` (string) - The name of the object you wish to upload.
    
- `object_extension` (string) - The file extension of the object (e.g., `txt`, `jpg`).
    
- `object_type_id` (string) - The ID of the object type, which categorizes the object being uploaded.
    
- `object_body` (string) - The content of the object in JSON format, which may include key-value pairs relevant to the object.
    
- `object_meta` (string) - Metadata associated with the object in JSON format, providing additional context or information about the object.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| object_name | True | `Required` |
| object_meta | True | `Required` |
| object_extension | True | `Required` |
| object_type_id | True | `Required` |
| object_body | True | `Required` |
| encrypt | True | `Optional` |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "object_name": "create and upload",
  "object_extension": "txt",
  "object_type_id": "7e46e7f9-15d4-41b6-83b9-a652336793ec",
  "object_body": "{\"key\": \"value\"}",
  "object_meta": "{\"meta1\":{\"key1\":\"value1\",\"key2\":\"value3\"}}"
}
```

Saved example: Create and Upload — HTTP 200
Top-level response keys: data, status
Data keys: meta_id
Envelope http_code: 200

### Object Storage / Object Profile Usages

ID: `46206122-ed7d1f29-aabb-43d3-a7bd-21a8aa6184ad`

`GET {{baseUrl}}/api/v1/resources/object_profile_usages?object_id=Object ID`

This endpoint retrieves the usage details of a specific object profile based on the provided `object_id`. It is useful for obtaining insights into how an object profile is being utilized within the system.

### Request Parameters

- **object_id** (required): The unique identifier of the object whose profile usages you want to retrieve. This should be passed as a query parameter in the URL.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| object_id | False | `Required` |

**Body template** (`json`; chưa phải payload runnable):

```text

```

Saved example: Create and Upload — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Object Storage / Get list of object types

ID: `46206122-3d65bbf5-b7b8-4f51-8c76-443655e04bd1`

`GET https://api.multilogin.com/api/v1/resources/types`

This endpoint makes an HTTP GET request to retrieve the resource types available.

Saved example: Get list of object types — HTTP 200
Top-level response keys: status, data
Data keys: types
Envelope http_code: 200

### Object Storage / Get Statistics for Objects

ID: `46206122-e3d5d553-9a32-4d47-8bb4-b5ed6c5c09d6`

`GET https://api.multilogin.com/api/v1/resources/statistics`

This endpoint allows you to retrieve statistics for the available resources.

Saved example: Get Statistics for Objects — HTTP 200
Top-level response keys: status, data
Data keys: global_count, global_count_limit, global_size, global_size_limit, object_types
Envelope http_code: 200

### Object Storage / Get Objects meta

ID: `46206122-4cd1bee6-c007-4223-8aa9-09c22c0e0504`

`GET https://api.multilogin.com/api/v1/resources/metas`

This endpoint makes an HTTP GET request to retrieve metas from the specified resource.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| limit | True | `Required`. Specify the number of objectsyou want to display. Default is `10`. |
| offset | True | `Required`. Specify the number of objects to skip from the beginning of the returned data before displaying the results. 0 means starting from the beginning. Defaults to `0`. |
| object_name | True | `Optional`. Specify the name of the objects you want to dispaly. |
| object_type_id | True | `Optional`. Specify the object type you want to display. |
| storage_type | True | `Optional`. Specify the storage type you want to display. |
| creator | True | `Optional`. Specify the UUID of the creator of the objects you want to dispaly. |
| trashbin | True | `Optional`. Specify if you want to see either the objects inside the trashbin or the ones that are available. Default is `false`. |
| create_start_date | True | `Optional`. Specify the create date of the objects. |
| create_end_date | True | `Optional`. Specify the end date of the objects. |
| update_start_date | True | `Optional`. Specify the update date of the objects. |
| update_end_date | True | `Optional`. Specify the end update date of the objects. |

Saved example: Get Objects Meta — HTTP 200
Top-level response keys: status, data
Data keys: objects
Envelope http_code: 0

### Object Storage / Get Object meta by ID

ID: `46206122-13c3f32c-b913-4694-9629-e06a066caba5`

`GET https://api.multilogin.com/api/v1/resources/:id/meta`

This endpoint retrieves the meta data for a specific resource identified by its unique ID.

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| id | False | `Required`. Specify the id of the object. |

Saved example: Get Objects Meta — HTTP 200
Top-level response keys: status, data
Data keys: id, meta_info, object_type_id, object_name, object_size, current_version, created_at, update_at, storage_type, created_by, update_by
Envelope http_code: 0

### Object Storage / Delete Object

ID: `46206122-bdc981a9-33f5-4c0e-a97c-7a71171e067d`

`GET https://api.multilogin.com/api/v1/resources/:id/delete`

This endpoint sends an HTTP GET request to delete a specific resource identified by the resource ID.

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| id | False | `Required`. Specify the id of the object. |

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| permanently | True | `Optional`. Specify the boolean value to either delete the object to trashbin or permanently. Default to `false`. |

Saved example: Delete Object — HTTP 200
Top-level response keys: status, data
Envelope http_code: 0

### Object Storage / Restore Object

ID: `46206122-f309afe7-44fd-4b5a-bd81-d77184def52a`

`GET https://api.multilogin.com/api/v1/resources/:id/restore`

This endpoint makes an HTTP GET request to retrieve a specific resource by its ID and restore it. The request does not include a request body, and the resource ID is specified in the URL. The response will include the details of the restored resource.

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| id | False | `Required`. Specify the id of the object. |

Saved example: Restore Object — HTTP 200
Top-level response keys: status, data
Envelope http_code: 0

### Object Storage / Cloud to Local

ID: `46206122-23510378-947d-4a6b-aaf6-8977385a535f`

`POST https://launcher.mlx.yt:45001/api/v1/object_storage/local_to_cloud`

This endpoint is used to transfer a local object to cloud storage.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| object_id | True | `Required`. Specify the id of the object. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "object_id": "<string>"
}
```

Saved example: Cloud to Local — HTTP 200
Top-level response keys: status
Envelope http_code: 0

### Object Storage / Local to Cloud

ID: `46206122-7853c39d-c3fa-49fc-8897-fa3dbd2c5b84`

`POST https://launcher.mlx.yt:45001/api/v1/object_storage/local_to_cloud`

This endpoint is used to transfer an object from local storage to cloud storage.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| object_path | True | `Required`. Specify the path to the object. |
| object_id | True | `Required`. Specify the id of the object. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "object_path": "<string>",
  "object_id": "<string>"
}
```

Saved example: Local to Cloud — HTTP 200
Top-level response keys: status, data
Data keys: meta_id
Envelope http_code: 0

### Object Storage / Download Object

ID: `46206122-5cab148b-d09f-44c6-b09b-05db8dedc3f3`

`GET https://launcher.mlx.yt:45001/api/v1/object_storage/<id_upload>/download`

This endpoint sends an HTTP GET request to retrieve the object storage data for a specific upload ID. The response of this request is a JSON schema representing the object storage data.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| id_upload | True | `Required`. Specify the id of the object. |

Saved example: Get Object meta by ID — HTTP 200
Top-level response keys: status
Envelope http_code: 0

### Object Storage / Create Extension

ID: `46206122-a8ec3021-44b1-435a-8adc-4c4305ca64f6`

`POST https://launcher.mlx.yt:45001/api/v1/create_extension_from_url`

This endpoint is used to create an extension from a given URL.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| url | True | `Required`. The url to the extension. |
| browser_type | True | `Required`. Specify the browser type. Note that the browser type should be the same as the extension you want to use. |
| storage_type | True | `Required`, specify the storage type. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "url": "<string>",
  "browser_type": "<value>",
  "storage_type": "<value>"
}
```

Saved example: Create Extension — HTTP 200
Top-level response keys: status
Envelope http_code: 0

### Object Storage / Enable Extension

ID: `46206122-94158628-d498-42c3-834b-25403217814d`

`POST https://api.multilogin.com/api/v1/resources/<object_id>/enable_for_profiles`

This endpoint enables the specified object for the associated profiles.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| object_id | True | `Required`. Specify the object id of the extension. |
| profile_ids | True | `Required`. Specify the profiles you want to apply the extension on. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "profile_ids": [
    "profile_id"
  ]
}
```

Saved example: Enable Extension — HTTP 200
Top-level response keys: status, data
Envelope http_code: 0

### Object Storage / Disable Extension

ID: `46206122-a15b0e07-8e3a-403d-966e-c30ea25ad3db`

`POST https://api.multilogin.com/api/v1/resources/<object_id>/disable_for_profiles`

This endpoint makes an HTTP POST request to disable a resource for specific profiles.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_ids | True | `Required`. Specify the profiles you want to disable the extension on. |
| object_id | True | `Required`. Specify the id of the extension you want to disable. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "profile_ids": [
    "<profile_id>"
  ]
}
```

Saved example: Disable Extension — HTTP 200
Top-level response keys: status, data
Envelope http_code: 0

### Object Storage / List of Objects per profile

ID: `46206122-921f5a01-de1c-4034-b5c0-f9d4d5fc47b8`

`POST https://api.multilogin.com/api/v1/resources/profile_object_usages`

This endpoint allows you to retrieve the usage statistics for a specific profile object.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| object_type | True | `Required`. Specify the object type. |
| profile_id | True | `Required`. Specify the profile id you want to check. |

**Body template** (`json`; chưa phải payload runnable):

```text

```

Saved example: List of Objects per profile — HTTP 200
Top-level response keys: status, data
Envelope http_code: 0

### Bookmark Management / Export Bookmarks

ID: `46206122-85f9ef09-4a7a-43f4-a0ea-14a5a9390f15`

`GET https://launcher.mlx.yt:45001/api/v1/profile/:profile_id/bookmarks/export`

Export bookmarks from a given profile.

Bookmarks are exported by default to the following directories:

- Windows: `C:\Users\%username%\mlx\bookmarks`
    
- macOS: `/Users/%username%/mlx/bookmarks`
    
- Linux: `/home/%username%/mlx/bookmarks`

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | False | `Required`. Specify the profile ID to export bookmarks. |

Saved example: Bookmarks Exported — HTTP 200
Top-level response keys: data, status
Data keys: path
Envelope http_code: 200

### Bookmark Management / Import Bookmarks

ID: `46206122-c30e40c5-cbd8-419b-8c0f-511a314c7eae`

`POST https://launcher.mlx.yt:45001/api/v1/profile/:profile/bookmarks/import`

Import bookmarks into a profile.

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile | False |  |

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| paths | True | `Required`. Path to a JSON file containing bookmarks |
| operation | True | `Required`. Specify what to do with exported bookmarks. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "paths": [
    "string" // a path to a JSON file containing bookmarks.
  ],
  "operation": "override" // Possible values are 'override' and 'append'
}
```

Saved example: Bookmarks Imported — HTTP 200
Top-level response keys: status
Envelope http_code: 200

### Bookmark Management / Copy Bookmarks

ID: `46206122-614114ea-3a51-481e-b53e-4136a24109cf`

`POST https://launcher.mlx.yt:45001/api/v1/profile/:profile_id/bookmarks/copy/:source_profile_id`

Copy bookmarks from one profile to another.

**pathVariables**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | False | `Required`. Specify profile_id |
| source_profile_id | False | `Required`. Specify source_profile_id |

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| paths | True | `Optional`. Path to a JSON file containing bookmarks. |
| operation | True | `Required`. Specify what to do with exported bookmarks. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
  "paths": [
    "string" // a path to a JSON file containing bookmarks.
  ],
  "operation": "override" // Possible values are 'override' and 'append'
}
```

Saved example: Bookmarks Copied — HTTP 200
Top-level response keys: status
Envelope http_code: 200

### 2FA / Set up 2FA

ID: `46206122-8044c4c8-9154-4cf6-baf5-eb3958546b45`

`POST https://api.multilogin.com/user/setup_2fa`

This endpoint is used to retrieve the response for setting up two-factor authentication for a user.

In the response, the user will receive the following JSON values:

``` json
"device_id": "UUID",
"otp_url_bytes": "enconded url in bytes"

 ```

- `device_id`: A unique identifier for the device, required to enable two-factor authentication (2FA).
    
- `otp_url_bytes`: A URL encoded in bytes that must be decoded to generate a QR code.
    

The decoded URL is used to display a QR code, which the user scans with their authenticator app to set up and view the one-time password (OTP) codes.

The user must set up a device on every workspace he joins that has the 2FA enabled.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| device_name | True | `Required`. This is the name of the device you want to set up 2FA on. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "device_name": "<string>"
}
```

Saved example: Set up 2FA — HTTP 200
Top-level response keys: status, data
Data keys: device_id, otp_url_bytes
Envelope http_code: 200

### 2FA / Enable 2FA

ID: `46206122-7fb03b1b-8d4c-4ad8-ba5d-f1dbefb2ff59`

`POST https://api.multilogin.com/user/enable_2fa`

This endpoint is used to retrieve the response for setting up two-factor authentication for a user.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| device_id | True | `Required`. This is the id from the response of "Set up 2FA". |
| totp_code | True | `Required`. This is the code from your 2FA app. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "device_id": "<string>",
    "totp_code": "<string>"
}
```

Saved example: Enable 2FA — HTTP 200
Top-level response keys: status, data
Data keys: backup_codes
Envelope http_code: 200

### 2FA / Verify 2FA

ID: `46206122-9ca41d72-7769-4bbc-922e-1ad1e852d7b0`

`POST https://api.multilogin.com/user/verify_2fa_otp`

This endpoint is used to initiate the setup process for a user's two-factor authentication (2FA).  
  
Once the user successfully verifies the 2FA setup, they will receive the same response as the Sign-In endpoint.  
  
This response includes the authentication token, which can be used to access other protected endpoints.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| temp_token | True | `Required`. After 2FA is enabled, when the user logs in he will get a temporary token instead of the normal token. |
| totp_code | True | `Required`. This is the code from your 2FA app. |
| is_backup | True | `Required`. If the values is set to `false`, the user needs to put the OTP code from app inside the "totp_code", otherwise the backup codes needs to be added. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "temp_token": "<string>",
    "totp_code": "<string>",
    "is_backup": <boolean>
}
```

Saved example: Verify 2FA — HTTP 200
Top-level response keys: status, data
Data keys: refresh_token, token
Envelope http_code: 200

### 2FA / Set up new device for 2FA

ID: `46206122-06f8c547-bdbb-4f67-8954-24e5cae5ddc8`

`POST https://api.multilogin.com/user/add_2fa_device`

To set up a new device for two-factor authentication, you need a `device_id`, which is provided in the response from the "Set up 2FA" endpoint.  
  
You can register multiple devices using this endpoint, with a maximum limit of 10 devices per user.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| device_id | True | `Required`. This is the id from the response of "Set up 2FA". |
| totp_code | True | `Required`. This is the code from your 2FA app. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "device_id": "<string>",
    "totp_code": "<string>"
}
```

Saved example: Set up new device for 2FA — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### 2FA / Get Devices for 2FA

ID: `46206122-db5dc409-1625-4659-ae09-56b6f12b306d`

`GET https://api.multilogin.com/user/get_2fa_devices`

This endpoint returns a list of all devices registered for two-factor authentication (2FA) for the user.  
  
Each entry in the response includes the `device_id` and `name` associated with the device.

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "device_id": "<string>",
    "totp_code": "<string>"
}
```

Saved example: Get Devices for 2FA — HTTP 200
Top-level response keys: status, data
Data keys: devices
Envelope http_code: 200

### 2FA / Get Backup Codes for 2FA

ID: `46206122-7998c668-a1db-449b-a15f-831304849e74`

`GET https://api.multilogin.com/user/backup_codes`

This endpoint returns a list of all available backup codes for the user's two-factor authentication (2FA).  
  
Please note that each backup code can be used only once. Once a code is used, it becomes invalid and will no longer appear in the response.

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "device_id": "<string>",
    "totp_code": "<string>"
}
```

Saved example: Get Devices for 2FA — HTTP 200
Top-level response keys: status, data
Data keys: backup_codes
Envelope http_code: 200

### 2FA / Revoke device for 2FA

ID: `46206122-cac06c29-9685-4338-841e-281a0af302c3`

`POST https://api.multilogin.com/user/revoke_2fa_device`

This endpoint allows you to revoke a specific device by providing its `device_id`.  
  
You can revoke multiple devices, but at least one 2FA device must remain active at all times.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| device_id | True | `Required`. This is the id from the response of "Set up 2FA" or from "Get Devices for 2FA. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "device_id": "<string>"
}
```

Saved example: Revoke device for 2FA — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### 2FA / Enable/Disable 2FA for Workspace

ID: `46206122-530c716b-7def-4b3d-a010-f1d931cf6ee5`

`POST https://api.multilogin.com/workspace/update_2fa`

This endpoint enables or disables two-factor authentication (2FA) for the workspace, depending on the specified configuration.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| enable | True | `Required`. This will enable or disable 2FA for the workspace. |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "enable": <boolean>
}
```

Saved example: Enable/Disable 2FA for Workspace — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### 2FA / Disable 2FA

ID: `46206122-c79b5767-c04c-4a12-84f8-1e737331efdb`

`POST https://api.multilogin.com/user/disable_2fa`

This endpoint disables two-factor authentication (2FA) for the user, based on the user identified from the provided token.  
**Note:** 2FA must be disabled at the workspace level before this endpoint can be used successfully.

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| enable | True | `Required`. This will enable or disable 2FA for the workspace. |

**Body template** (`json`; chưa phải payload runnable):

```text

```

Saved example: Disable 2FA — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Mobile Profile Management/ADB / Mobile Profile ADB Set

ID: `46206122-8c147c3f-973f-4ade-96f0-e4ee2b37ea03`

`POST https://api.multilogin.com/mobile_profiles/phone/adb/set`

<p>Enable or disable Android Debug Bridge (ADB) on the provided running cloud phones.</p><p>Up to 50 IDs per request (duplicates are removed). The phone must be running - start it first with <strong>Mobile Profile Start</strong>. Non-running profiles are excluded and reported in <code>fail_details</code> with an error code and message.</p><p>After enabling ADB, retrieve the connection details with <strong>Mobile Profile ADB Info</strong>.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. cloud phone IDs (max 50) |
| enabled | True | `Required`. desired ADB state: `true` enables ADB, `false` disables it |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "ids": [
        "619005104636297579",
        "618154668161237077"
    ],
    "enabled": true
}
```

Saved example: ADB State Set — HTTP 200
Top-level response keys: status, data
Data keys: total_amount, success_amount, fail_amount, success_details, fail_details
Envelope http_code: 200

### Mobile Profile Management/ADB / Mobile Profile ADB Info

ID: `46206122-7d0bc183-8e74-4cf0-9e2f-b5dc30828244`

`POST https://api.multilogin.com/mobile_profiles/phone/adb/info`

<p>Retrieve per-profile ADB connection details (<code>ip</code>, <code>port</code>, <code>pwd</code>) for the provided cloud phones.</p><p>Up to 50 IDs per request. The endpoint is idempotent and has no side effects on the ADB state.</p><p>Per-profile <code>status</code> values: <code>active</code> - ADB is running and <code>ip</code> / <code>port</code> / <code>pwd</code> are populated; <code>disabled</code> - the phone is stopped or ADB is not enabled; <code>error</code> - unsupported or unknown.</p><p>Use the returned values with your ADB client: <code>adb connect ip:port</code>, then authenticate with <code>pwd</code>.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. cloud phone IDs (max 50) |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "ids": [
        "619005104636297579",
        "618154668161237077"
    ]
}
```

Saved example: ADB Info Retrieved — HTTP 200
Top-level response keys: status, data
Data keys: items
Envelope http_code: 200

### Mobile Profile Management / Mobile Profile List

ID: `46206122-2baa5c32-a2a8-4b19-91cd-0c9be258f4a7`

`GET https://api.multilogin.com/mobile_profiles/phone/list?page=1&page_size=50`

<p>Retrieve a paginated list of mobile profiles (cloud phones) in the workspace.</p><p>All filters are optional and can be combined. Results are paginated: use <code>page</code> and <code>page_size</code> to navigate.</p><p>Check out <strong>Params</strong> to see what each query parameter is about.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| page | False | `Optional`. page number, starts at 1 (default 1) |
| page_size | False | `Optional`. items per page, maximum 100 (default 50) |
| serial_name | True | `Optional`. filter by profile name; partial match is supported |
| remark | True | `Optional`. filter by remark |
| ids | True | `Optional`. profile IDs to fetch; repeat the parameter for each ID, e.g. `ids=123&ids=234` |
| folder_id | True | `Optional`. filter by folder ID |
| serial_numbers | True | `Optional`. filter by serial numbers; repeat the parameter for each value |
| tags | True | `Optional`. filter by tag IDs; repeat the parameter for each value |
| usecase_name | True | `Optional`. filter by usecase name |
| sort | True | `Optional`. sort direction: `asc` (A-Z) or `desc` (Z-A) |
| order_by | True | `Optional`. field to sort by: `name`, `created_at`, `updated_at` or `last_launched_at`; defaults to `name` |
| adb_status | True | `Optional`. filter by ADB state: `active` or `disabled`; omit to show all profiles |
| is_running | True | `Optional`. if `true`, return only running profiles; if `false`, only stopped ones |
| favorite_filter | True | `Optional`. filter by favorite status: `personal`, `workspace` or `both` |

Saved example: Profiles Found — HTTP 200
Top-level response keys: status, data
Data keys: total, page, page_size, items
Envelope http_code: 200

### Mobile Profile Management / Mobile Profile Create

ID: `46206122-aded28d9-64cd-4a14-a8b9-41c667e05d84`

`POST https://api.multilogin.com/mobile_profiles/phone/create`

<p>Create one or more cloud phone profiles of the specified mobile type.</p><p>Each entry in <code>data</code> describes one profile batch; use <code>quantity</code> to create several profiles from the same entry - each gets its own serial number and device identity.</p><p>The phone number is auto-generated if not provided. A proxy is required: pass a connection string in <code>proxy_information</code> or reference an MLX-managed ISP proxy via <code>isp_ip_id</code>.</p><p>Use <strong>Phone Brand List</strong> to discover valid <code>surface_brand_name</code> / <code>surface_model_name</code> values and <strong>States by Country</strong> / <strong>Cities by State</strong> for geo fields.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| mobile_type | True | `Required`. mobile OS type, e.g. `Android 14`; supported Android versions: 12-16 |
| data | True | `Required`. profile definitions; at least one entry |
| data[].profile_name | True | `Required`. profile name |
| data[].proxy_information | True | `Required`. proxy connection string, e.g. `socks5://user:pass@host:1080`; not needed when `isp_ip_id` is set |
| folder_id | True | `Optional`. folder to create the profiles in |
| data[].quantity | True | `Optional`. number of profiles to create from this entry (default 1) |
| data[].isp_ip_id | True | `Optional`. MLX-managed ISP proxy ID; attaches the managed proxy instead of `proxy_information` |
| data[].phone_name | True | `Optional`. phone device name |
| data[].phone_number | True | `Optional`. mobile phone number; auto-generated if empty |
| data[].profile_note | True | `Optional`. profile note |
| data[].mobile_region / mobile_province / mobile_city | True | `Optional`. geo location of the device |
| data[].mobile_language | True | `Optional`. device language, e.g. `en` |
| data[].net_type | True | `Optional`. networking type: `0` = Wi-Fi, `1` = Mobile (default); supported on Android 12/13/15 |
| data[].surface_brand_name / surface_model_name | True | `Optional`. device brand and model to mimic |
| data[].tags | True | `Optional`. tag IDs to assign on creation |
| data[].usecase_id | True | `Optional`. usecase to attach |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "mobile_type": "Android 14",
    "folder_id": "ec273d2c-f03e-46bc-b005-52b1ed3a575b",
    "data": [
        {
            "profile_name": "my-phone",
            "proxy_information": "socks5://proxy-user:proxy-pass@gate.example.com:1080",
            "quantity": 1,
            "mobile_region": "New York",
            "mobile_language": "en",
            "net_type": 1,
            "tags": [
                "0197c9a0-3f65-7a2e-9c17-5d84a1b0c2d3"
            ]
        }
    ]
}
```

Saved example: Profiles Created — HTTP 200
Top-level response keys: status, data
Data keys: total_amount, success_amount, fail_amount, details
Envelope http_code: 200

### Mobile Profile Management / Mobile Profile Update

ID: `46206122-b8a2fe9e-1cee-4e3f-b16d-4c1f84bd0b7b`

`PUT https://api.multilogin.com/mobile_profiles/phone/update`

<p>Update the name, folder, remark, phone number, proxy configuration, usecase or tags of an existing mobile profile.</p><p>Only <code>id</code> is required; other fields are optional and only the fields you provide are updated.</p><p>Proxy can be set three ways: reference a saved proxy with <code>proxy_id</code>, attach an MLX-managed ISP proxy with <code>isp_ip_id</code>, or pass connection parameters in <code>proxy_config</code>.</p><p><strong>NB: tags use partial-update semantics</strong> - omit the field (or send <code>null</code>) to keep the current tags, send <code>[]</code> to clear them, or send a list of tag IDs to replace them.</p><p>The response returns the updated profile entity in <code>data.profile</code>.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| id | True | `Required`. mobile profile ID |
| name | True | `Optional`. profile name |
| folder_id | True | `Optional`. move the profile to this folder |
| remark | True | `Optional`. profile remark (short description) |
| phone_number | True | `Optional`. mobile phone number |
| usecase_id | True | `Optional`. usecase to attach |
| proxy_id | True | `Optional`. saved proxy ID |
| isp_ip_id | True | `Optional`. MLX-managed ISP proxy ID; connection parameters are resolved server-side |
| proxy_config | True | `Optional`. manual proxy settings, see below |
| proxy_config.use_proxy_cfg | True | `Optional`. required inside `proxy_config`; if `true`, reuse the already-configured dynamic proxy settings |
| proxy_config.type_id | True | `Optional`. required inside `proxy_config`; proxy type: `1` = SOCKS5, `2` = HTTP, `3` = HTTPS, `20` = IPIDEA, `21` = IPHTML, `22` = Kookeey, `23` = Lumatuo |
| proxy_config.protocol | True | `Optional`. proxy protocol: `1` = SOCKS5, `2` = HTTP |
| proxy_config.server / port / username / password | True | `Optional`. proxy connection parameters |
| proxy_config.country / region / city | True | `Optional`. geo selection for dynamic proxy types |
| tags | True | `Optional`. tag IDs; partial-update semantics as described above |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "id": "619005104636297579",
    "name": "my-phone",
    "folder_id": "ec273d2c-f03e-46bc-b005-52b1ed3a575b",
    "remark": "staging device",
    "proxy_config": {
        "use_proxy_cfg": false,
        "type_id": 1,
        "protocol": 1,
        "server": "gate.example.com",
        "port": 1080,
        "username": "proxy-user",
        "password": "proxy-pass"
    },
    "tags": [
        "0197c9a0-3f65-7a2e-9c17-5d84a1b0c2d3",
        "0197c9a0-4b12-7f08-8a55-90e2c7d64f18"
    ]
}
```

Saved example: Profile Updated — HTTP 200
Top-level response keys: status, data
Data keys: fail_details, profile
Envelope http_code: 200

### Mobile Profile Management / Mobile Profile Delete

ID: `46206122-d8c7331d-1e12-4fc6-ad03-0314fed92fd6`

`DELETE https://api.multilogin.com/mobile_profiles/phone/delete`

<p>Permanently delete one or more mobile profiles by their IDs.</p><p><strong>NB: deleted profiles cannot be recovered.</strong></p><p>The operation returns a summary of successful and failed deletions. Failed entries include an error code and message explaining why the deletion was rejected.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. mobile profile IDs to delete |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "ids": [
        "619005104636297579",
        "618154668161237077"
    ]
}
```

Saved example: Profiles Deleted — HTTP 200
Top-level response keys: status, data
Data keys: total_amount, success_amount, fail_amount, fail_details
Envelope http_code: 200

### Mobile Profile Management / Mobile Profile Statuses

ID: `46206122-8d0f2380-f8ae-48c1-aa1d-71d65f349865`

`POST https://api.multilogin.com/mobile_profiles/phone/statuses`

<p>Retrieve the current runtime status of one or more mobile profiles.</p><p>Status codes: <code>0</code> - Started, <code>1</code> - Starting, <code>2</code> - Shut down (idle), <code>3</code> - Expired.</p><p>The response includes a summary (total / success / fail counts) and per-profile details: status, running time, ADB state and scheduled auto-stop time. Profiles that could not be queried appear in <code>fail_details</code> with an error code and message. Running-only fields (<code>running_time_secs</code>, <code>auto_stopped_at</code>) are omitted for stopped phones.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. mobile profile IDs |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "ids": [
        "619005104636297579",
        "618154668161237077"
    ]
}
```

Saved example: Statuses Retrieved — HTTP 200
Top-level response keys: status, data
Data keys: total_amount, success_amount, fail_amount, success_details, fail_details
Envelope http_code: 200

### Mobile Profile Management / Mobile Profile Start

ID: `46206122-03c8a2b2-204a-49b9-968b-34b96cc72c6b`

`POST https://api.multilogin.com/mobile_profiles/phone/start`

<p>Start one or more cloud phones without a graphical interface.</p><p>The response reports how many phones were successfully started and lists any failures with error details. For each started phone a streaming URL is returned.</p><p><strong>NB: even though the phone starts without GUI, plan minutes are still consumed while it is running.</strong></p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. cloud phone IDs to start |
| hide_side_bar | True | `Optional`. hide the sidebar in the streaming view |
| display_timer | True | `Optional`. display the running timer |
| width | True | `Optional`. cloud phone display width in px |
| center | True | `Optional`. center the cloud phone display |
| hide_library | True | `Optional`. hide the Asset Library (Material Center) |
| material_tag_ids | True | `Optional`. tag IDs used to pre-filter the Asset Library |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "ids": [
        "619005104636297579",
        "618154668161237077"
    ]
}
```

Saved example: Phones Started — HTTP 200
Top-level response keys: status, data
Data keys: total_amount, success_amount, success_details, fail_amount, fail_details
Envelope http_code: 200

### Mobile Profile Management / Mobile Profile Stop

ID: `46206122-f1c96cdc-024d-45e6-acf1-098f8367074c`

`POST https://api.multilogin.com/mobile_profiles/phone/stop`

<p>Stop one or more cloud phones.</p><p>The response reports how many phones were successfully stopped and lists any failures with error details.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. cloud phone IDs to stop |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "ids": [
        "619005104636297579",
        "618154668161237077"
    ]
}
```

Saved example: Phones Stopped — HTTP 200
Top-level response keys: status, data
Data keys: total_amount, success_amount, fail_amount, fail_details
Envelope http_code: 200

### Mobile Profile Management / Mobile Profile Export

ID: `46206122-4218eee1-8085-4a06-a7db-01c6ff8b643c`

`POST https://api.multilogin.com/mobile_profiles/phone/export`

<p>Export the data of one or more mobile profiles to an Excel (.xlsx) file.</p><p>The file contains profile details including device info, proxy configuration and metadata.</p><p>Minimum 1 and maximum 200 profile IDs per export.</p><p>The response body is the binary .xlsx file (content type <code>application/vnd.openxmlformats-officedocument.spreadsheetml.sheet</code>).</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_ids | True | `Required`. mobile profile IDs to export (min 1, max 200) |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "profile_ids": [
        "619005104636297579",
        "618154668161237077"
    ]
}
```

Saved example: Export File — HTTP 200

### Mobile Profile Management / Mobile Profile Transfer

ID: `46206122-06683087-bbcc-4391-ac71-658ff01e8e46`

`POST https://api.multilogin.com/folder/phone/transfer`

<p>Transfer ownership of one or more mobile profiles to another user in the workspace, identified by their email address.</p><p>The target user must be a member of the same workspace. The effective limit per call is min(200, workspace plan limit).</p><p><strong>NB: ownership transfer is immediate and cannot be undone.</strong></p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. mobile profile IDs to transfer (min 1, max 200, capped by the plan limit) |
| target_email | True | `Required`. destination user email |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "ids": [
        "619005104636297579"
    ],
    "target_email": "colleague@example.com"
}
```

Saved example: Profiles Transferred — HTTP 200
Top-level response keys: status, data
Data keys: 
Envelope http_code: 200

### Mobile Profile Management / Mobile Profile Group Get or Create

ID: `46206122-f9e67f4f-6fc1-41a3-acbf-f0bb75f24624`

`GET https://api.multilogin.com/mobile_profiles/group/get_or_create`

<p>Return the mobile profile group of the current workspace. If no group exists yet, one is created automatically.</p><p>Every workspace has exactly one mobile profile group. The group ID is used when batch-installing apps (see <strong>Mobile App Install</strong>).</p><p>This endpoint takes no parameters.</p>

Saved example: Group Retrieved — HTTP 200
Top-level response keys: status, data
Data keys: id, name, remark
Envelope http_code: 200

### Mobile Profile Management / Mobile Profile Tag Assign

ID: `46206122-82565563-8731-40bb-9ff1-fbde3ebff5e8`

`POST https://api.multilogin.com/mobile_profiles/tag/assign`

<p>Assign one or more tags to a mobile profile by tag ID.</p><p>Tags must already exist in the workspace (create them with <strong>Tag Create</strong> in Profile Management). Up to 10 tags can be assigned per call.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | True | `Required`. mobile profile ID |
| tags | True | `Required`. tag IDs to assign (max 10) |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "profile_id": "619005104636297579",
    "tags": [
        "0197c9a0-3f65-7a2e-9c17-5d84a1b0c2d3",
        "0197c9a0-4b12-7f08-8a55-90e2c7d64f18"
    ]
}
```

Saved example: Tags Assigned — HTTP 200
Top-level response keys: status, data
Data keys: 
Envelope http_code: 200

### Mobile Profile Management / Mobile Profile Tag Unassign

ID: `46206122-268dcb8d-8fa2-4ffa-8fab-f8f2e47de921`

`POST https://api.multilogin.com/mobile_profiles/tag/unassign`

<p>Remove one or more tags from a mobile profile by tag ID.</p><p>Up to 10 tags can be removed per call. Only tags currently assigned to the profile are affected.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| profile_id | True | `Required`. mobile profile ID |
| tags | True | `Required`. tag IDs to remove (max 10) |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "profile_id": "619005104636297579",
    "tags": [
        "0197c9a0-3f65-7a2e-9c17-5d84a1b0c2d3"
    ]
}
```

Saved example: Tags Unassigned — HTTP 200
Top-level response keys: status, data
Data keys: 
Envelope http_code: 200

### Mobile Profile Management / Mobile File Tag Assign

ID: `46206122-7e687ceb-160c-4c7c-b73a-4612167d198b`

`POST https://api.multilogin.com/mobile_profiles/files/tag/assign`

<p>Assign one or more tags to a file stored on the mobile profile drive, by tag ID.</p><p><code>material_id</code> is the file ID obtained from <strong>Mobile File List</strong> or returned by <strong>Mobile File Upload</strong>.</p><p>Up to 10 tags can be assigned per call. Tags must already exist in the workspace.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| material_id | True | `Required`. file ID |
| tags | True | `Required`. tag IDs to assign (max 10) |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "material_id": "0197d1e2-8c40-7b91-b3aa-6f02e58a9c47",
    "tags": [
        "0197c9a0-3f65-7a2e-9c17-5d84a1b0c2d3"
    ]
}
```

Saved example: Tags Assigned — HTTP 200
Top-level response keys: status, data
Data keys: 
Envelope http_code: 200

### Mobile Profile Management / Mobile File Tag Unassign

ID: `46206122-539f3d57-e15e-4476-8575-8e25352dae93`

`POST https://api.multilogin.com/mobile_profiles/files/tag/unassign`

<p>Remove one or more tags from a file stored on the mobile profile drive, by tag ID.</p><p><code>material_id</code> is the file ID obtained from <strong>Mobile File List</strong>.</p><p>Up to 10 tags can be removed per call. Only tags currently assigned to the file are affected.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| material_id | True | `Required`. file ID |
| tags | True | `Required`. tag IDs to remove (max 10) |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "material_id": "0197d1e2-8c40-7b91-b3aa-6f02e58a9c47",
    "tags": [
        "0197c9a0-3f65-7a2e-9c17-5d84a1b0c2d3"
    ]
}
```

Saved example: Tags Unassigned — HTTP 200
Top-level response keys: status, data
Data keys: 
Envelope http_code: 200

### Mobile Profile Management / Mobile Profile Limit

ID: `46206122-1732c709-e445-4116-91a7-871d3f0c9c90`

`GET https://api.multilogin.com/mobile_profiles/limit`

<p>Show the current mobile allowance metering for the workspace.</p><p>Returns the active metric - currently per-minute billing (<code>per_minute_billing_with_inheritance</code>): minutes used, the plan limit and the remaining allowance.</p><p>This endpoint takes no parameters.</p>

Saved example: Limit Retrieved — HTTP 200
Top-level response keys: status, data
Data keys: current_used_value, metric_code, metric_limit, remaining_limit
Envelope http_code: 200

### Mobile Profile Management / Mobile Proxy Check

ID: `46206122-29cf1250-bbff-463a-b759-0fe9d91c937a`

`POST https://api.multilogin.com/mobile_profiles/proxy/check`

<p>Test whether a proxy is reachable and retrieve its geo-location details.</p><p>Returns the outbound IP with country, subdivision, city, ISP and timezone as detected by the specified detection service.</p><p>Pass connection parameters (<code>proxy_type</code>, <code>server</code>, <code>port</code> and credentials), or set <code>isp_ip_id</code> to check an MLX-managed ISP proxy - in that case the connection parameters are resolved server-side and can be omitted.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| detect_type | True | `Required`. detection service, e.g. `IP2Location` |
| proxy_type | True | `Optional`. proxy protocol: `socks5` or `http`; required unless `isp_ip_id` is set |
| server | True | `Optional`. proxy server address; required unless `isp_ip_id` is set |
| port | True | `Optional`. proxy port; required unless `isp_ip_id` is set |
| username | True | `Optional`. proxy username |
| password | True | `Optional`. proxy password |
| isp_ip_id | True | `Optional`. MLX-managed ISP proxy ID to check instead of explicit connection parameters |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "detect_type": "IP2Location",
    "proxy_type": "socks5",
    "server": "gate.example.com",
    "port": 1080,
    "username": "proxy-user",
    "password": "proxy-pass"
}
```

Saved example: Proxy Checked — HTTP 200
Top-level response keys: status, data
Data keys: detect_status, message, outbound_ip, country_code, country_name, subdivision, city, timezone, isp
Envelope http_code: 200

### Mobile Profile Management / States by Country

ID: `46206122-547f39ef-fb2b-450e-9cdb-f9a3c598b77a`

`GET https://api.multilogin.com/mobile_profiles/states_by_country?country=USA`

<p>List all states / regions available for a given country.</p><p>Use the country code (e.g. <code>USA</code>, <code>GBR</code>). The returned state names can be passed to <strong>Cities by State</strong> and used in the geo fields of profile create / update.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| country | False | `Required`. country code, e.g. `USA` |

Saved example: States Found — HTTP 200
Top-level response keys: status, data
Data keys: country, states
Envelope http_code: 200

### Mobile Profile Management / Cities by State

ID: `46206122-8101a8c1-16f5-4c17-8d62-887723e8f1d5`

`GET https://api.multilogin.com/mobile_profiles/cities_by_state?state=California`

<p>List all cities available for a given state / region.</p><p>Use a state name returned by <strong>States by Country</strong> (e.g. <code>California</code>). The returned city names can be used in the geo fields of profile create / update.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| state | False | `Required`. state name, e.g. `California` |

Saved example: Cities Found — HTTP 200
Top-level response keys: status, data
Data keys: state, cities
Envelope http_code: 200

### Mobile Profile Management / Phone Brand List

ID: `46206122-75ed6b87-6376-4d55-bdbc-0d9f6ff47a48`

`POST https://api.multilogin.com/mobile_profiles/phone/brand/list`

<p>List all available phone brands and models for a given Android version.</p><p>Use the returned brand and model names in the <code>surface_brand_name</code> / <code>surface_model_name</code> fields of <strong>Mobile Profile Create</strong>.</p><p>Supported Android versions: 12, 13, 14, 15, 16.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| android_version | True | `Required`. Android version: 12, 13, 14, 15 or 16 |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "android_version": 14
}
```

Saved example: Brands Found — HTTP 200
Top-level response keys: status, data
Envelope http_code: 200

### Mobile Profile Management / Import Template Download

ID: `46206122-b553a591-37f2-4801-bc12-0e9dccf54b7b`

`GET https://api.multilogin.com/mobile_profiles/phone/import/template`

<p>Download the official Excel (.xlsx) template used for bulk mobile profile import.</p><p>Fill in the template with your profile data, then check it with <strong>Import File Validate</strong> before confirming the import.</p><p>The response body is the binary .xlsx file (content type <code>application/vnd.openxmlformats-officedocument.spreadsheetml.sheet</code>). This endpoint takes no parameters.</p>

Saved example: Template File — HTTP 200

### Mobile Profile Management / Import File Validate

ID: `46206122-dd510814-de14-4dc7-90e0-60e12b272253`

`POST https://api.multilogin.com/mobile_profiles/phone/import/validate`

<p>Validate an Excel file containing mobile profile data without creating any profiles.</p><p>Each row is checked and a per-row pass / fail report is returned together with a <code>validation_id</code>. No data is persisted at this stage.</p><p>Use the <code>validation_id</code> with the import confirm step to create the profiles: only rows that passed validation will be created; invalid rows are skipped.</p><p>The request is <code>multipart/form-data</code>.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| file | True | `Required`. the filled-in Excel (.xlsx) template |

**Body template** (`formdata`; chưa phải payload runnable):

```text
[{'type': 'file', 'key': 'file', 'src': [], 'description': 'Excel file with mobile profile data'}]
```

Saved example: File Validated — HTTP 200
Top-level response keys: status, data
Data keys: validation_id, total_rows, valid_rows, invalid_rows, rows
Envelope http_code: 200

### Mobile Profile Management / Mobile File Upload

ID: `46206122-d35c2709-fc2c-4e32-b68a-eadb04fc4282`

`POST https://api.multilogin.com/mobile_profiles/files/upload`

<p>Upload a file to the shared mobile profile drive of the workspace.</p><p>Supported file types: jpg, jpeg, png, gif, bmp, webp, heif, heic, mp4, webm, apk, xapk, xml.</p><p>Returns a <code>material_id</code> that can be used with <strong>Mobile File Tag Assign</strong>.</p><p>The request is <code>multipart/form-data</code>.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| file | True | `Required`. the file to upload |

**Body template** (`formdata`; chưa phải payload runnable):

```text
[{'type': 'file', 'key': 'file', 'src': [], 'description': 'File to upload to the mobile profile drive'}]
```

Saved example: File Uploaded — HTTP 200
Top-level response keys: status, data
Data keys: material_id
Envelope http_code: 200

### Mobile Profile Management / Mobile File List

ID: `46206122-dadf36fd-ba0e-4acc-9f08-b2ef09021960`

`POST https://api.multilogin.com/mobile_profiles/files/list`

<p>List files uploaded to the mobile profile drive of the workspace.</p><p><code>page</code> and <code>page_size</code> are required. Use <code>file_name</code> to filter by name and <code>file_type</code> to filter by type.</p><p>The file <code>id</code> from the output is used with <strong>Mobile File Tag Assign</strong> and <strong>Mobile File Delete</strong>.</p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| page | True | `Required`. page number, starts at 1 |
| page_size | True | `Required`. items per page |
| file_name | True | `Optional`. filter by file name |
| file_type | True | `Optional`. filter by file type: `1` = image, `2` = video / app |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "page": 1,
    "page_size": 20,
    "file_name": "",
    "file_type": [
        1
    ]
}
```

Saved example: Files Found — HTTP 200
Top-level response keys: status, data
Data keys: total, page, page_size, list
Envelope http_code: 200

### Mobile Profile Management / Mobile File Delete

ID: `46206122-c246fc93-fc31-49e6-ab2e-baea7c15a375`

`POST https://api.multilogin.com/mobile_profiles/files/delete`

<p>Delete one or more files from the mobile profile drive by their file IDs.</p><p>File IDs are obtained from <strong>Mobile File List</strong>.</p><p><strong>NB: deletion is immediate and cannot be undone.</strong></p><p>Check out <strong>Params</strong> to see what each parameter is about.</p><p>To copy the example request body, navigate to <strong>Body</strong>.</p>

**queryParams**

| Tên | Disabled | Mô tả |
|---|---|---|
| ids | True | `Required`. file IDs to delete |

**Body template** (`json`; chưa phải payload runnable):

```text
{
    "ids": [
        "0197d1e2-8c40-7b91-b3aa-6f02e58a9c47"
    ]
}
```

Saved example: Files Deleted — HTTP 200
Top-level response keys: status, data
Data keys: 
Envelope http_code: 200
