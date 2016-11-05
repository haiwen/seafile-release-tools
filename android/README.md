## Use it on a local machine

- Put the keyfile google-api-key.json under the android/ directory.
- Run the script:

```sh
./android/publish_apk.py --local-publish
./android/publish_apk.py --local-publish --version 1.2.3 # publish a specific version
```

## Travis CI

Create a tag and push it to github. The travis ci build would publish the latest released apk on github to google play.
