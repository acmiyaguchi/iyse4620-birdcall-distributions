<script>
  import { onMount } from "svelte";
  import EarthEngineMatter from "$lib/docs/EarthEngineMatter.md";

  const url =
    import.meta.env.VITE_HOST ||
    "https://storage.googleapis.com/iyse6420-birdcall-distribution/processed";

  let manifest = {};

  let mapIndex = 0;
  let shouldLogScale = false;

  $: maps = manifest.maps || [];
  $: features = manifest.feature_names || [];

  onMount(async () => {
    const res = await fetch(`${url}/earth_engine/manifest.json`);
    manifest = await res.json();
  });
</script>

<EarthEngineMatter />

<h2>Options</h2>
<div class="menu">
  <div class="bordered">
    <!-- make radio button for an option -->
    <b>region and resolution: </b>
    {#each maps as map, index}
      <label>
        <input type="radio" name="map" bind:group={mapIndex} value={index} />
        {map.region}, {map.grid_size}&deg;</label
      >
    {/each}
  </div>
  <!-- checkbox for should log or not -->
  <div class="bordered">
    <b>plot scale</b>
    <label>
      <input type="checkbox" bind:checked={shouldLogScale} />
      display in log scale
    </label>
  </div>
</div>

<h2>Plots</h2>

{#if maps.length > 0}
  <h3>{maps[mapIndex].region}, {maps[mapIndex].grid_size}&deg; resolution</h3>
{/if}

<div class="images">
  {#each features as name}
    {@const mapName = `${maps[mapIndex].region}_${maps[mapIndex].grid_size}`}
    {@const imgName = shouldLogScale ? `log_${name}` : name}
    <img src="{url}/earth_engine/{mapName}/{imgName}.png" alt={imgName} />
  {/each}
</div>

<style>
  .images {
    text-align: center;
    font-size: 0;
  }
  img {
    width: 320px;
  }

  /* add padding between menu items */
  .menu > div {
    padding: 5px;
    max-width: 600px;
  }
  .bordered {
    /* make these so they have a thin border */
    border: 1px solid black;
  }
</style>
