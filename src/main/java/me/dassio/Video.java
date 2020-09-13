package me.dassio;

import java.net.URL;
import java.util.Date;

public class Video {
	private String name;
	private URL url;
	private URL thumbnail;
	private String description;
	private Date uploadedTime;
	private Integer watchedTimes;



	/**
	 * Get name.
	 *
	 * @return name as String.
	 */
	public String getName()
	{
		return name;
	}

	/**
	 * Set name.
	 *
	 * @param name the value to set.
	 */
	public void setName(String name)
	{
		this.name = name;
	}

	/**
	 * Get url.
	 *
	 * @return url as URL.
	 */
	public URL getUrl()
	{
		return url;
	}

	/**
	 * Set url.
	 *
	 * @param url the value to set.
	 */
	public void setUrl(URL url)
	{
		this.url = url;
	}

	/**
	 * Get thumbnail.
	 *
	 * @return thumbnail as URL.
	 */
	public URL getThumbnail()
	{
		return thumbnail;
	}

	/**
	 * Set thumbnail.
	 *
	 * @param thumbnail the value to set.
	 */
	public void setThumbnail(URL thumbnail)
	{
		this.thumbnail = thumbnail;
	}

	/**
	 * Get description.
	 *
	 * @return description as String.
	 */
	public String getDescription()
	{
		return description;
	}

	/**
	 * Set description.
	 *
	 * @param description the value to set.
	 */
	public void setDescription(String description)
	{
		this.description = description;
	}

	/**
	 * Get uploadedTime.
	 *
	 * @return uploadedTime as Date.
	 */
	public Date getUploadedTime()
	{
		return uploadedTime;
	}

	/**
	 * Set uploadedTime.
	 *
	 * @param uploadedTime the value to set.
	 */
	public void setUploadedTime(Date uploadedTime)
	{
		this.uploadedTime = uploadedTime;
	}

	/**
	 * Get watchedTimes.
	 *
	 * @return watchedTimes as Integer.
	 */
	public Integer getWatchedTimes()
	{
		return watchedTimes;
	}

	/**
	 * Set watchedTimes.
	 *
	 * @param watchedTimes the value to set.
	 */
	public void setWatchedTimes(Integer watchedTimes)
	{
		this.watchedTimes = watchedTimes;
	}
}
