package me.dassio;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.GenerationType;
import javax.persistence.Id;


@Entity
class Credential {
	
	@Id
	@GeneratedValue(strategy = GenerationType.AUTO)
	private Integer id;

	private String accessToken;

	private String refreshToken;
	
	public Credential() {
	}

	public Credential(String accessToken,String refreshToken){
		this.accessToken = accessToken;
		this.refreshToken = refreshToken;
	}
	/**
	 * Set refreshToken.
	 *
	 * @param refreshToken the value to set.
	 */
	public void setRefreshToken(String refreshToken)
	{
	    this.refreshToken = refreshToken;
	}
	
	/**
	 * Get refreshToken.
	 *
	 * @return refreshToken as String.
	 */
	public String getRefreshToken()
	{
	    return refreshToken;
	}
	
	/**
	 * Set accessToken.
	 *
	 * @param accessToken the value to set.
	 */
	public void setAccessToken(String accessToken)
	{
	    this.accessToken = accessToken;
	}
	
	/**
	 * Get accessToken.
	 *
	 * @return accessToken as String.
	 */
	public String getAccessToken()
	{
	    return accessToken;
	}
	
	/**
	 * Get id.
	 *
	 * @return id as Integer.
	 */
	public Integer getId()
	{
	    return id;
	}
	
	/**
	 * Set id.
	 *
	 * @param id the value to set.
	 */
	public void setId(Integer id)
	{
	    this.id = id;
	}
}
