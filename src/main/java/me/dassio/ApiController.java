package me.dassio;

import java.util.ArrayList; 
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ApiController {

 // private final ArrayList<Channel> channels;
  //private final YoutubeClient client;

//  @GetMapping("/channels")
//  public ArrayList<Channel> getChannels() {
//    return client.getChannels();
//  }
//
//  public ArrayList<Video> getChannelVideos{
//     return channel.getVideos();
//  }
		
		@GetMapping("/")
	public String index() {
		return "welcome to Youtube2Youku";
	} 
//
}
