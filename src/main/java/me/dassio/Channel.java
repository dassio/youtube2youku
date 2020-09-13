package me.dassio;

import java.net.URL;

public class Channel {
  private String channelId;
	private String titile;
  private URL avatar;

   public URL getAvatar() {
    return avatar;
  }
  
  /**
   * Get channelId.
   *
   * @return channelId as String.
   */
  public String getChannelId()
  {
      return channelId;
  }
  
  /**
   * Set channelId.
   *
   * @param channelId the value to set.
   */
  public void setChannelId(String channelId)
  {
      this.channelId = channelId;
  }
	
	/**
	 * Get titile.
	 *
	 * @return titile as String.
	 */
	public String getTitile()
	{
	    return titile;
	}
	
	/**
	 * Set titile.
	 *
	 * @param titile the value to set.
	 */
	public void setTitile(String titile)
	{
	    this.titile = titile;
	}
}


