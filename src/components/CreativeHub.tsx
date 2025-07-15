
import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Music, 
  Palette, 
  BookOpen, 
  Heart,
  Play,
  Pause,
  Volume2,
  Headphones,
  Sparkles,
  Camera,
  Wand2
} from 'lucide-react';

const CreativeHub = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTrack, setCurrentTrack] = useState('Robin Serenity Mix');

  const musicLibrary = [
    {
      title: 'Robin Serenity Mix',
      species: 'American Robin',
      duration: '3:24',
      mood: 'Calming',
      description: 'Harmonized territorial calls designed to reduce stress'
    },
    {
      title: 'Sparrow Social Symphony',
      species: 'House Sparrow',
      duration: '2:45',
      mood: 'Peaceful',
      description: 'Community chirping patterns for relaxation'
    },
    {
      title: 'Hawk Warning Harmony',
      species: 'Red-tailed Hawk',
      duration: '4:12',
      mood: 'Alert',
      description: 'Structured alert calls for controlled bird dispersal'
    }
  ];

  const birdStories = [
    {
      title: 'The Tale of Alpha Robin',
      character: 'Dominant Male Robin',
      chapter: 'Chapter 3: Territory Expansion',
      summary: 'After successfully defending his nesting area, Alpha Robin begins expanding his territory toward the runway approach zone...',
      emotion: 'Confident',
      lastUpdate: '2 hours ago'
    },
    {
      title: 'The Sparrow Parliament',
      character: 'Social Sparrow Flock',
      chapter: 'Chapter 1: The Great Gathering',
      summary: 'A unprecedented meeting of three sparrow flocks occurs near Terminal B, with complex negotiations over feeding rights...',
      emotion: 'Diplomatic',
      lastUpdate: '4 hours ago'
    }
  ];

  const visualArt = [
    {
      title: 'Morning Symphony Visualization',
      source: 'Robin territorial calls (6:30 AM)',
      style: 'Flowing waves in blue and gold',
      description: 'Sound frequencies transformed into flowing organic patterns'
    },
    {
      title: 'Migration Route Mandala',
      source: 'Seasonal migration data',
      style: 'Circular pattern in earth tones',
      description: 'Flight paths converted to intricate geometric art'
    },
    {
      title: 'Emotional Color Map',
      source: 'Daily emotional states',
      style: 'Abstract color field',
      description: 'Bird emotions represented through dynamic color gradients'
    }
  ];

  const getMoodColor = (mood: string) => {
    switch (mood) {
      case 'Calming': return 'bg-blue-100 text-blue-800';
      case 'Peaceful': return 'bg-green-100 text-green-800';
      case 'Alert': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Creative Features Overview */}
      <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
        <CardHeader>
          <CardTitle className="flex items-center text-xl">
            <Sparkles className="w-6 h-6 mr-3 text-purple-500" />
            Creative AI Hub - Where Science Meets Art
          </CardTitle>
          <CardDescription>
            Transforming bird data into music, stories, and visual art to bridge human-avian understanding
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4">
              <Music className="w-8 h-8 mx-auto mb-2 text-blue-500" />
              <h3 className="font-semibold">Music Composition</h3>
              <p className="text-sm text-slate-600">Species-specific calming melodies</p>
            </div>
            <div className="text-center p-4">
              <BookOpen className="w-8 h-8 mx-auto mb-2 text-green-500" />
              <h3 className="font-semibold">Behavioral Stories</h3>
              <p className="text-sm text-slate-600">Individual bird narratives</p>
            </div>
            <div className="text-center p-4">
              <Palette className="w-8 h-8 mx-auto mb-2 text-purple-500" />
              <h3 className="font-semibold">Visual Art</h3>
              <p className="text-sm text-slate-600">Sound and data visualizations</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Creative Content Tabs */}
      <Tabs defaultValue="music" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="music" className="flex items-center space-x-2">
            <Music className="w-4 h-4" />
            <span>Music Composer</span>
          </TabsTrigger>
          <TabsTrigger value="stories" className="flex items-center space-x-2">
            <BookOpen className="w-4 h-4" />
            <span>Story Generator</span>
          </TabsTrigger>
          <TabsTrigger value="art" className="flex items-center space-x-2">
            <Palette className="w-4 h-4" />
            <span>Visual Art</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="music">
          <div className="space-y-6">
            {/* Music Player */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Headphones className="w-5 h-5 mr-2 text-blue-500" />
                  Bird Music Composition Engine
                </CardTitle>
                <CardDescription>
                  AI-generated melodies based on bird call patterns and emotional states
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg mb-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold">{currentTrack}</h3>
                      <p className="text-slate-600">Harmonized bird calls for stress reduction</p>
                    </div>
                    <Button 
                      onClick={() => setIsPlaying(!isPlaying)}
                      className="bg-gradient-to-r from-blue-500 to-purple-600"
                    >
                      {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    </Button>
                  </div>
                  
                  {/* Mock waveform */}
                  <div className="h-16 flex items-end space-x-1 mb-4">
                    {Array.from({ length: 40 }, (_, i) => (
                      <div
                        key={i}
                        className="bg-gradient-to-t from-blue-400 to-purple-500 rounded-t-sm flex-1"
                        style={{ height: `${Math.random() * 100}%` }}
                      />
                    ))}
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-slate-600">
                    <span>1:24</span>
                    <span>Calming • Robin-based</span>
                    <span>3:24</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Music Library */}
            <Card>
              <CardHeader>
                <CardTitle>AI Music Library</CardTitle>
                <CardDescription>Species-specific compositions for various scenarios</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {musicLibrary.map((track, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:bg-slate-50 transition-colors">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-lg flex items-center justify-center">
                          <Music className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <div className="font-medium">{track.title}</div>
                          <div className="text-sm text-slate-600">{track.species} • {track.duration}</div>
                          <div className="text-xs text-slate-500">{track.description}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getMoodColor(track.mood)}>{track.mood}</Badge>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => setCurrentTrack(track.title)}
                        >
                          <Play className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="stories">
          <div className="space-y-6">
            {/* Story Generator */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Wand2 className="w-5 h-5 mr-2 text-green-500" />
                  AI Story Generator
                </CardTitle>
                <CardDescription>
                  Creating narratives from real bird behavior data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <Button className="bg-gradient-to-r from-green-500 to-teal-600">
                    <Sparkles className="w-4 h-4 mr-2" />
                    Generate New Story
                  </Button>
                  <p className="text-sm text-slate-600 mt-2">
                    Create a new story based on current bird activity
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Active Stories */}
            <Card>
              <CardHeader>
                <CardTitle>Ongoing Bird Stories</CardTitle>
                <CardDescription>Real-time narratives generated from bird behavior</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {birdStories.map((story, index) => (
                    <div key={index} className="p-6 border rounded-lg bg-gradient-to-r from-slate-50 to-green-50">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-lg font-semibold text-slate-800">{story.title}</h3>
                          <p className="text-green-600 font-medium">{story.character}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className="bg-green-100 text-green-800">{story.emotion}</Badge>
                          <span className="text-xs text-slate-500">{story.lastUpdate}</span>
                        </div>
                      </div>
                      
                      <div className="mb-3">
                        <span className="text-sm font-medium text-blue-600">{story.chapter}</span>
                      </div>
                      
                      <p className="text-slate-700 mb-4">{story.summary}</p>
                      
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline">
                          <BookOpen className="w-3 h-3 mr-1" />
                          Read Full Story
                        </Button>
                        <Button size="sm" variant="outline">
                          <Heart className="w-3 h-3 mr-1" />
                          Follow Character
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="art">
          <div className="space-y-6">
            {/* Art Generator */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Camera className="w-5 h-5 mr-2 text-purple-500" />
                  Data-to-Art Converter
                </CardTitle>
                <CardDescription>
                  Transform bird calls and behavior data into visual art
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Button variant="outline" className="h-24 flex-col">
                    <Volume2 className="w-6 h-6 mb-2" />
                    <span className="text-xs">Sound Waves</span>
                  </Button>
                  <Button variant="outline" className="h-24 flex-col">
                    <Heart className="w-6 h-6 mb-2" />
                    <span className="text-xs">Emotions</span>
                  </Button>
                  <Button variant="outline" className="h-24 flex-col">
                    <Music className="w-6 h-6 mb-2" />
                    <span className="text-xs">Migration Paths</span>
                  </Button>
                  <Button variant="outline" className="h-24 flex-col">
                    <Sparkles className="w-6 h-6 mb-2" />
                    <span className="text-xs">Behavior Patterns</span>
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Art Gallery */}
            <Card>
              <CardHeader>
                <CardTitle>AI Art Gallery</CardTitle>
                <CardDescription>Visual representations of bird data and behavior</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {visualArt.map((artwork, index) => (
                    <div key={index} className="border rounded-lg overflow-hidden">
                      <div className="aspect-square bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100 flex items-center justify-center">
                        <Palette className="w-16 h-16 text-purple-400" />
                      </div>
                      <div className="p-4">
                        <h3 className="font-semibold mb-1">{artwork.title}</h3>
                        <p className="text-sm text-slate-600 mb-2">{artwork.description}</p>
                        <div className="text-xs text-slate-500">
                          <div>Source: {artwork.source}</div>
                          <div>Style: {artwork.style}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CreativeHub;
