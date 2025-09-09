declare module 'react-leaflet-cluster' {
  import * as React from 'react';
  import { MarkerClusterGroupOptions } from 'leaflet';

  interface MarkerClusterGroupProps extends MarkerClusterGroupOptions {
    children: React.ReactNode;
  }

  class MarkerClusterGroup extends React.Component<MarkerClusterGroupProps> {}

  export default MarkerClusterGroup;
}