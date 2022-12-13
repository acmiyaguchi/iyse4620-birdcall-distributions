<script>
  import { onMount } from "svelte";

  const url =
    import.meta.env.VITE_HOST ||
    "https://storage.googleapis.com/iyse6420-birdcall-distribution/processed";

  let manifest = {};
  $: maps = manifest.maps;
  $: features = manifest.feature_names || [];

  onMount(async () => {
    const res = await fetch(`${url}/earth_engine/manifest.json`);
    manifest = await res.json();
  });
</script>

{JSON.stringify(manifest)}

<div class="images">
  {#each features as name}
    <img src="{url}/earth_engine/{maps[0].region}_{maps[0].grid_size}/{name}.png" alt={name} />
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
</style>
