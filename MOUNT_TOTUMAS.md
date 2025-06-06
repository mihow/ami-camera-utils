# Procedure for Mount Totumas research trip

## Requirements
Make sure you have Python and Poetry installed on your machine.

## Backup and prepare images from SD cards

We keep 2 copies of images on external drives. One with original photos (MT_original) and one with images prepared for Antenna (MT_prepared). For syncing, we use the `rsync` command to only transfer the differences between files.

Folder structure for MT_original:
```
totumas
  2025
    entocam-1
    entocam-2
    entocam-4
    entocam-5
    entocam-6
```

Folder structure for MT_prepared:
```
totumas
  2025
    entocam-1
    entocam-2
    entocam-4
    entocam-5
    entocam-6
    snapshots
      entocam-1
      entocam-2
      entocam-4
      entocam-5
      entocam-6
```

### Sync original photos to MT_original
To sync files from a card i to the drive with original photos:
```
rsync -rva /Volumes/GardePro/DCIM/ /Volumes/MT_original/totumas/2025/entocam-[i]
```

Do this for each card and make sure to replace the `i` with the card number!

### Sync and prepare images to MT_prepared
On MT_prepared we also keep original images, but renamed to match Antenna requirements (timestamp included in the filename). We also keep a folder with 10 minute snapshots, to be used for quick processing.

To install script requirements:
```
poetry install
```

To rename images:
```
poetry run photo-renamer --prefix entocam[i] '/Volumes/MT_original/totumas/2025/entocam-[i]' --output-dir '/Volumes/MT_pepared/totumas/2025/entocam-[i]'
```

To generate 10 minute snapshots:
```
poetry run photo-sampler '/Volumes/MT_pepared/totumas/2025/entocam-[i]' --output-dir '/Volumes/MT_pepared/totumas/2025/snapshots/entocam-[i]'
```

Do this for each card and make sure to replace the `i` with the card number!

### Upload snapshots to the shared storage
1. Use Cyberduck (or a similar tool) to connect to the shared S3 storage on Compute Canada.
2. Go to the `/ami-trapdata/totumas/2025` folder
3. Right click folder `snapshots`, choose action "Syncronize", pick local `snapshots` folder

A confirmation dialog will open.

4. Ensure the top option is set to "Upload".
5. Click "Continue".

## Sync and process captures on Antenna
1. Go to Antenna and the list of stations. For each station, open the edit dialog, go to tab "Source image collection" and click "Sync now". We can also do this in bulk from admin.
2. Go to Antenna and the list of collections. For each collection, click "Populate". This will make the new captures considered for the upcoming processing. 
3. Go to Django admin and the list of deployments. Select all deployments, pick the action "Regroup captures into events" and click "Go". This will generate sessions on Antenna. In future, this manual step will not be needed.
4. Go to Antenna and the list of jobs. For each station, create a job to process the captures. Set source image collection to the station captures. Set pipeline to "Panama Plus Species Classifier with OOD detection - Mar 2025".
