import type { CSSProperties } from 'react'

// Local demo film only (/public/film). Not an official team page.
export const BG_IMAGE_1 = '/film/stance.jpg' // ready stance — BASE, always visible
export const BG_IMAGE_2 = '/film/point.jpg' // #4 point + mouthpiece — REVEAL inside spotlight

export const FOOTER_FILM = [
  { src: '/film/tunnel.jpg', cap: 'TUNNEL' }, // IMG_6778 pack (#0/#73)
  { src: '/film/stance.jpg', cap: 'STANCE' },
  { src: '/film/point.jpg', cap: 'POINT' },
  { src: '/film/leap.jpg', cap: 'LEAP' },
  { src: '/film/belt.jpg', cap: 'BELT' },
  { src: '/film/roar.jpg', cap: 'ROAR' },
  { src: '/film/look.jpg', cap: 'LOOK' }, // IMG_6627 #1 looking up
] as const

export const layerStyle = (src: string): CSSProperties => ({
  backgroundImage: `url(${src})`,
  backgroundSize: 'cover',
  backgroundPosition: 'center top',
  backgroundRepeat: 'no-repeat',
})
