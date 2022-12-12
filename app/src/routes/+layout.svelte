<script>
  import NavBar from "$lib/NavBar.svelte";
  import { page } from "$app/stores";

  export let data;
  $: client_status = data && data.client_status;
</script>

<NavBar
  path={$page.url.pathname
    .split("/")
    .slice(1)
    .map((s) => s.trim())
    .filter((s) => s)}
  {client_status}
/>

<slot />
