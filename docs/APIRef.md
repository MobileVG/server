# API 参考文档

## API 公用参数

在调用每个API时，都需要附加一些参数，这些参数如下:

<table>
<thead>
    <tr>
        <th>Name</th>
        <th>Type</th>
        <th>Description</th>
    </tr>
</thead>
<tbody>
    <tr>
        <td>X-VG-App</td>
        <td>Header</td>
        <td>App ID</td>
    </tr>
    <tr>
        <td>X-VG-Secret</td>
        <td>Header</td>
        <td>App 密码</td>
    </tr>
    <tr>
        <td>X-VG-Device</td>
        <td>Header</td>
        <td>设备信息</td>
    </tr>
    <tr>
        <td>X-VG-AppVersion</td>
        <td>Header</td>
        <td>App的版本码（整数）</td>
    </tr>
    <tr>
        <td>X-VG-Locale</td>
        <td>Header</td>
        <td>App的Locale信息</td>
    </tr>
</tbody>
</table>

## Buy

### /buy/user/identify

标识用户并且进行登录


