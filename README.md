# android-a2p
Simple huristic based Android api to permission mapping extractor. (incomplete but accurate)

Research results like [PScout](http://pscout.csl.toronto.edu/) are more complete but imprecise and problematic. For security checkers like Android capability leak, those result are not able to be used in the practical.

This inspires me to do the simple huristic python script, and results are surprisingly good.

If you find any new case not covered by the script please let me know, or feel free to push-request your code.

## Observation
AOSP have following ways to describe the permission needed for an API:

1. Annotation [@RequiresPermission](https://developer.android.com/reference/android/support/annotation/RequiresPermission.html):
```java
@RequiresPermission( allOf = {
        Manifest.permission.INTERACT_ACROSS_USERS_FULL,
        Manifest.permission.MANAGE_USERS
})
public @Nullable String getUserAccount(@UserIdInt int userHandle) {
    try {
        return mService.getUserAccount(userHandle);
    } catch (RemoteException re) {
        throw re.rethrowFromSystemServer();
    }
}
```
This tells us the `getUserAccount` API need `INTERACT_ACROSS_USERS_FULL` and (&) `MANAGE_USERS` permission.
Other variaties are, `anyOf` means `or (|)`, single permission.

2. JavaDoc `{@link android.Manifest.permission#XXX}`:
```java
/**
 * Returns list of the profiles of userHandle including
 * userHandle itself.
 * Note that this returns both enabled and not enabled profiles. See
 * {@link #getEnabledProfiles(int)} if you need only the enabled ones.
 *
 * Requires {@link android.Manifest.permission#MANAGE_USERS} permission.
 * @param userHandle profiles of this user will be returned.
 * @return the list of profiles.
 * @hide
 */
public List<UserInfo> getProfiles(@UserIdInt int userHandle) {
    try {
        return mService.getProfiles(userHandle, false /* enabledOnly */);
    } catch (RemoteException re) {
        throw re.rethrowFromSystemServer();
    }
}
```
This tells us `getProfiles` API need `MANAGE_USERS` permission.

## Implementation
Regex based python script:

1. Build permission short name to full name mapping via parse `android/Manifest.java`:
```java
public static final java.lang.String ACCESS_CHECKIN_PROPERTIES = "android.permission.ACCESS_CHECKIN_PROPERTIES";
```
Generate: `ACCESS_CHECKIN_PROPERTIES -> android.permission.ACCESS_CHECKIN_PROPERTIES`

2. Walkthrough each **.java** file under base directory:

- a. Extract package name (e.g. `android.os`) and class name (e.g. `UserManager`).
- b. Apply `Observation 1 and 2` to find method name to permission mappings (e.g. `getProfiles -> MANAGE_USERS`).
- c. Find full name for permission (e.g. `MANAGE_USERS` to `android.permission.MANAGE_USERS`).
- d. Build record (e.g. `android.os.UserManager getProfiles android.permission.MANAGE_USERS`).

## Interpret
`android.permission.MANAGE_USERS` means it only requires one permission.

`android.permission.INTERACT_ACROSS_USERS_FULL|android.permission.MANAGE_USERS` means need any of those permissions.

`android.permission.INTERACT_ACROSS_USERS_FULL&android.permission.MANAGE_USERS` means need all of those permissions.

## Usage
```bash
$ python extract_permission_mapping.py <base_dir>
```

## A2P Mappings
[Android N](mapping_n.txt)
